# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp import addons
import logging
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import tools
import time
import math
from datetime import datetime
import datetime
from openerp import netsvc
import openerp.addons.decimal_precision as dp
from openerp import SUPERUSER_ID, netsvc
from urllib import urlencode
from urlparse import urljoin

class medical_certificate(osv.osv):
    _name = "medical.certificate"
    _description = "Medical Certificate"
    

    _columns = {

        'name':fields.char('Description'),
        'serial_no':fields.integer('Sr No'),
        'medical_certificate_number':fields.many2one('hr.holidays','Medical Certificate Number'),
        'medical_certificate_file':fields.binary('Medical Certificate'),
        
    }

class hr_employee_new(osv.osv):
    _name = "hr.employee.new"
    _description = "Employees Copy"
    
    
   
    _columns = {

        'name':fields.char('Name'),
        #'serial_no':fields.integer('Sr No'),
        'department_id':fields.many2one('hr.department','Department'),
        'emp_code':fields.char('Employee Code'),
        
        'join_date':fields.date('Date of Joining'),
        
        'image_new': fields.binary("Photo",
            help="This field holds the image used as photo for the employee, limited to 1024x1024px."),
        
        
    }
    
    def _get_default_image(self, cr, uid, context=None):
        image_path = addons.get_module_resource('zeeva_hr', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))

    _defaults = {
        'image_new': _get_default_image,
    }


class hr_employee(osv.osv):
    _name = "hr.employee"
    _description = "Employee"
    _inherit = ["hr.employee","mail.thread"]
    

    def _set_remaining_days(self, cr, uid, empl_id, name, value, arg, context=None):
        employee = self.browse(cr, uid, empl_id, context=context)
        diff = value - employee.remaining_leaves
        type_obj = self.pool.get('hr.holidays.status')
        holiday_obj = self.pool.get('hr.holidays')
        
        status_ids = type_obj.search(cr, uid, [('limit', '=', False)], context=context)
        if len(status_ids) != 1 :
            raise osv.except_osv(_('Warning!'),_("The feature behind the field 'Remaining Legal Leaves' can only be used when there is only one leave type with the option 'Allow to Override Limit' unchecked. (%s Found). Otherwise, the update is ambiguous as we cannot decide on which leave type the update has to be done. \nYou may prefer to use the classic menus 'Leave Requests' and 'Allocation Requests' located in 'Human Resources \ Leaves' to manage the leave days of the employees if the configuration does not allow to use this field.") % (len(status_ids)))
        status_id = status_ids and status_ids[0] or False
        if not status_id:
            return False
        if diff > 0:
            leave_id = holiday_obj.create(cr, uid, {'name': _('Allocation for %s') % employee.name, 'employee_id': employee.id, 'holiday_status_id': status_id, 'type': 'add', 'holiday_type': 'employee', 'number_of_days_temp': diff}, context=context)
        elif diff < 0:
            leave_id = holiday_obj.create(cr, uid, {'name': _('Leave Request for %s') % employee.name, 'employee_id': employee.id, 'holiday_status_id': status_id, 'type': 'remove', 'holiday_type': 'employee', 'number_of_days_temp': abs(diff)}, context=context)
        else:
            return False
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'confirm', cr)
        wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'validate', cr)
        wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'second_validate', cr)
        return True

    def _get_remaining_days(self, cr, uid, ids, name, args, context=None):
        cr.execute("""SELECT
                sum(h.number_of_days) as days,
                h.employee_id
            from
                hr_holidays h
                join hr_holidays_status s on (s.id=h.holiday_status_id)
            where
                h.state='validate' and
                s.limit=False and
                h.employee_id in (%s)
            group by h.employee_id"""% (','.join(map(str,ids)),) )
        res = cr.dictfetchall()
        remaining = {}
        for r in res:
            remaining[r['employee_id']] = r['days']
        for employee_id in ids:
            if not remaining.get(employee_id):
                remaining[employee_id] = 0.0
        return remaining

    def _get_leave_status(self, cr, uid, ids, name, args, context=None):
        holidays_obj = self.pool.get('hr.holidays')
        holidays_id = holidays_obj.search(cr, uid,
           [('employee_id', 'in', ids), ('date_from','<=',time.strftime('%Y-%m-%d %H:%M:%S')),
           ('date_to','>=',time.strftime('%Y-%m-%d 23:59:59')),('type','=','remove'),('state','not in',('cancel','refuse'))],
           context=context)
        result = {}
        for id in ids:
            result[id] = {
                'current_leave_state': False,
                'current_leave_id': False,
                'leave_date_from':False,
                'leave_date_to':False,
            }
        for holiday in self.pool.get('hr.holidays').browse(cr, uid, holidays_id, context=context):
            result[holiday.employee_id.id]['leave_date_from'] = holiday.date_from
            result[holiday.employee_id.id]['leave_date_to'] = holiday.date_to
            result[holiday.employee_id.id]['current_leave_state'] = holiday.state
            result[holiday.employee_id.id]['current_leave_id'] = holiday.holiday_status_id.id
        return result

    def _calculate_tenure(self, cr, uid, ids, join_date, arg, context=None):
        res = dict.fromkeys(ids, False)
        for ee in self.browse(cr, uid, ids, context=context):

            import datetime
            from datetime import datetime
            from datetime import timedelta
            from time import strftime
            from datetime import date

            from dateutil.relativedelta import relativedelta

            if ee.join_date:
                date_dt= datetime.strptime(ee.join_date, "%Y-%m-%d").date()
                today = datetime.today().date()
                tenure = relativedelta(today, date_dt)
                if tenure.years == 0:
                    res[ee.id] = "{0.months} month(s) {0.days} days ".format(tenure)
                else:
                    res[ee.id] = "{0.years} years {0.months} month(s) {0.days} days ".format(tenure)
        return res
    
    _columns = {
        'employee_number': fields.integer('Employee Number', size=32, help='Employee Unique Identification Number'),
        'join_date': fields.date('Date of Joining', size=32),
        'tenure': fields.function(_calculate_tenure, type='char', method=True, string = 'Tenure'),
        'casual_leaves': fields.float('Remaining Casual Leaves (CL)', size=32),
        'sick_leaves': fields.float('Remaining Sick Leaves (SL)', size=32),
        'compensatory_leaves': fields.float('Remaining Compensatory-Offs (CO)', size=32),
        'compensatory_table':fields.one2many('compensatory.leaves','compensatory_id','Availed Comp-Offs'),
        'trips_compensatory_table':fields.one2many('compensatory.leaves.trips','compensatory_trip_id','Currently Available Comp-Offs'),
        'no_of_confinements_post_joining':fields.integer('No of confinements post joining'),
        'employee_grade':fields.selection([('A1', 'A1'),('B1', 'B1'),('B2', 'B2'),('C1', 'C1'),('C2', 'C2'),('C3', 'C3')], 'Grade'),
        'status_of_confirmation': fields.char('Status of Confirmation'),
        'present_sick_leave':fields.float('Present Sick Leaves'),
        'past_sick_leave':fields.float('Past Sick Leaves'),
        
        
    }

hr_employee()

class trip_budget(osv.osv):
    _name = "trip.budget"
    _description = "Trip Planned Budget"
    

    _columns = {
    
        'budget_id':fields.many2one('hr.holidays','Budget Number'),
        'serial_no':fields.integer('Sr. No.'),
        'travel':fields.float('Travel', size=64),
        'lodging':fields.float('Lodging', size=64),
        #'date_against_which_co_taken':fields.date('Date against which CO is taken'),
        #'compensatory_expiry_date':fields.date('CO Expiry Date'),
        

    }

trip_budget()


class hr_holidays_status(osv.osv):
    _name = "hr.holidays.status"
    _inherit = "hr.holidays.status"

    _columns = {
        'business_trip':fields.boolean('Business Trip'),
    
    
    }

class employee_grade(osv.osv):
    _name = "employee.grade"
    _description = "Employee Grade"
    #_inherit = "hr.holidays.status"

    _columns = {
        'name':fields.selection([('A1', 'A1'),('B1', 'B1'),('B2', 'B2'),('C1', 'C1'),('C2', 'C2'),('C3', 'C3')], 'Name'),
        'description':fields.char('Description',size=64),
        'job_ids': fields.many2many('hr.job', 'grade_job_rel', 'grade_id', 'job_id', 'Designations'),
    
    
    }

class res_city(osv.osv):
    _name = "res.city"
    _description = "Cities/Towns"
    #_inherit = "hr.holidays.status"

    _columns = {
        'name':fields.char('City/Town',size=64),
        'state_name':fields.many2one('res.country.state','State',size=64),
        'country':fields.many2one('res.country','Country',size=64),
        'classification_level': fields.selection([('Metros', 'Metros'),('Tier1', 'Tier1'),('Tier2', 'Tier2'),('Other cities', 'Other cities')], 'Classification Level'),
        #'job_ids': fields.many2many('hr.job', 'grade_job_rel', 'grade_id', 'job_id', 'Designations'),
    
    
    }
    
class compensatory_leaves_table(osv.osv):
    _name = "compensatory.leaves.table"
    _description = "Compensatory Leaves Details"
    

    _columns = {

        'compensatory_id':fields.many2one('hr.holidays','Compensatory Number'),
        'serial_no':fields.integer('Sr No'),
        'compensatory_date':fields.date('Compensatory Leave Date'),
        'date_against_which_CO_taken':fields.date('Date against which CO is taken'),
        'compensatory_expiry_date':fields.date('CO Expiry Date'),
        

    }
    
    def onchange_date_against_which_CO_taken(self, cr, uid, ids, date_against_which_CO_taken):
        
        if date_against_which_CO_taken:
            
            

            co_date_year = int(date_against_which_CO_taken[:4])
            co_date_month = int(date_against_which_CO_taken[5:7])
            co_date_date = int(date_against_which_CO_taken[8:10])

            

            from dateutil.relativedelta import relativedelta

            import datetime
            from datetime import datetime
            from datetime import timedelta
            from time import strftime
            from datetime import date

            date_after_2months_from_co_date = date(co_date_year,co_date_month,co_date_date) + relativedelta(months=+2)
            values = {
                   'compensatory_expiry_date' : str(date_after_2months_from_co_date),
                    }

        return {'value' : values}

compensatory_leaves_table()



class hr_holidays(osv.osv):
    _name = "hr.holidays"
    _description = "Holidays"
    _inherit = "hr.holidays"

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name','trip_no'], context=context)
        res = []
        for record in reads:
            name = str(record['name'])
            if record['trip_no'] and name:
                name = name + ' ' + str(record['trip_no'])
                
            res.append((record['id'], name))
        return res
    
    def _employee_get(self, cr, uid, context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            return ids[0]
        return False
        
    def _get_employee_grade(self, cr, uid, context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        employee = self.pool.get('hr.employee').browse(cr, uid, ids[0])
        if ids:
            return employee.employee_grade.id
        return False
        
    def _check_date(self, cr, uid, ids):
        for holiday in self.browse(cr, uid, ids):
            holiday_ids = self.search(cr, uid, [('date_from', '<=', holiday.date_to), ('date_to', '>=', holiday.date_from), ('employee_id', '=', holiday.employee_id.id), ('id', '<>', holiday.id), ('state', '=', 'confirm')])
            if holiday_ids:
                return False
        return True
    
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'trip_no': self.pool.get('ir.sequence').get(cr, uid, 'hr.holidays'),
        })
        return super(hr_holidays, self).copy(cr, uid, id, default, context=context)

    def _planned_amount(self, cr, uid, ids, field_name, arg, context=None):
        res= {}
        for expense in self.browse(cr, uid, ids, context=context):
            total = 0.0
            for line in expense.planned_expense_line_details:
                total += line.unit_amount  * line.no_of_days
            res[expense.id] = total
        return res
        
    def _calculate_total_amount(self, cr, uid, ids, field_name, arg, context=None):
        res= {}
        for expense in self.browse(cr, uid, ids, context=context):
            total = 0.0
            for line in expense.planned_expense_line_details:
                total += line.unit_amount  * line.no_of_days
            res[expense.id] = total
        return res
        
    def _calculate_difference_amount(self, cr, uid, ids, field_name, arg, context=None):
        res= {}
        for expense in self.browse(cr, uid, ids, context=context):
            difference = 0.0
            #for line in expense.planned_expense_line_details:
            difference = expense.total_planned_amount  - expense.total_approved_amount
            res[expense.id] = difference
        return res    

    _columns = {
        'company_id':fields.many2one('res.company','Company'),
        'current_user':fields.many2one('res.users','Current User',size=32),
        'allow_leave_request':fields.boolean('Allow Leave Request on urgent basis'),
        'specify_reason_for_refusal':fields.boolean('Specify Reason for Refusal of Leave'),
        'date_against_which_CO_taken':fields.date('Date against which CO is taken'),
        'compensatory_expiry_date':fields.date('Compensatory Expiry Date'),
        'compensatory_dates_boolean':fields.boolean('Compensatory Dates checkbox'),
        'upload_medical_certificate':fields.boolean('Upload Medical Certificate'),
        'upload_maternity_certificate':fields.boolean('Upload an attachment'),
        'maternity_certificate':fields.binary('Maternity Certificate'),
        'show_remaining_leaves':fields.boolean('Show Remaining Leaves'),
        'upload_wedding_card':fields.boolean('Upload Wedding Card'),
        'wedding_card':fields.binary('Wedding Card'),
        'medical_certificate_line':fields.one2many('medical.certificate','medical_certificate_number','Medical Certificate',size=64),
        'remaining_privilege_leaves':fields.float('Remaining PLs', size=32),
        'remaining_casual_leaves':fields.float('Remaining CLs', size=32),
        'remaining_sick_leaves':fields.float('Remaining SLs', size=32),
        'remaining_compensatory_leaves':fields.float('Remaining COs', size=32),
        'reason_for_refusal':fields.text('Reason for Refusal of Leave'),
        'allow_leave_record_in_probationary_period':fields.boolean('Allow Leave Record to be created in Probationary Period'),
        'description':fields.text('Description'),
        'business_trip':fields.boolean('Business Trip'),
        'expense_approved':fields.boolean('Expense Approved'),
        'trip_budget':fields.one2many('trip.budget','budget_id','Trip Budget Details'),
        'gradewise_travel_details':fields.one2many('gradewise.mode.of.travel.details.budget','travel_id',''),
        'lodging_expenses_budget_details':fields.one2many('lodging.expenses.budget','lodging_expenses_id',''),
        'boarding_expenses_budget_details':fields.one2many('boarding.expenses.budget','boarding_expenses_id',''),
        'employee_grade':fields.selection([('A1', 'A1'),('B1', 'B1'),('B2', 'B2'),('C1', 'C1'),('C2', 'C2'),('C3', 'C3')], 'Grade'),
        'city':fields.many2one('res.city', 'City'),
        'travelled_city_line_details':fields.one2many('travelled.city.details','city_id',''),
        'planned_expense_line_details':fields.one2many('planned.budget.expenses','planned_budget_id',''),
        'compensatory_table':fields.one2many('compensatory.leaves.table','compensatory_id',''),
        'advance_amount_line_details':fields.one2many('advance.amount','advance_id',''),
        'planned_amount': fields.function(_planned_amount, string='Total Amount', digits_compute=dp.get_precision('Account'), store=True),
        'trip_no':fields.char('Trip No.'),
        'request_for_travelling_during_odd_hours': fields.boolean('Request for travelling during odd hours'),
        'travel_during_odd_hours_line':fields.one2many('travel.during.odd.hours','odd_hour_id',''),
        'send_business_trip_mail':fields.boolean('Send Business Trip mail'),
        'date_of_creation':fields.date('Date of Creation'),
        #'total_planned_amount':fields.float('Total Planned Expenses Amount'),
        'total_planned_amount':fields.function(_calculate_total_amount, type='float', string='Total Planned Expenses Amount'),
        'date_of_planned_amount':fields.date('Date'),
        'description_of_planned_amount':fields.text('Description/Remarks'),
        'total_approved_amount':fields.float('Total Approved Amount'),
        'difference_in_amount':fields.function(_calculate_difference_amount, type='float', string='Difference in Amounts'),
        'mode_of_payment_for_approved_amount':fields.selection([('Cash', 'Cash'),('Check', 'Check'),('NEFT', 'NEFT')], 'Mode of Payment'),
        'date_of_approved_amount':fields.date('Date of Approval'),
        'description_of_approved_amount':fields.text('Description/Remarks'),
        'reason_for_leave':fields.text('Reason for Leave'),
    }
    
    _defaults = {
        'current_user': lambda obj, cr, uid, ctx=None: uid,
        'employee_id': _employee_get,
        #'employee_grade': _get_employee_grade,
        'state': 'draft',
        'type': 'remove',
        'user_id': lambda obj, cr, uid, context: uid,
        'holiday_type': 'employee',
        'trip_no': lambda obj, cr, uid, context: '/',
        'date_of_creation': fields.date.context_today,
    }
    
    _constraints = [
        (_check_date, 'You can not have 2 leaves that overlaps on same day!', ['date_from','date_to']),
    ] 

    _sql_constraints = [
        ('name_trip_no_uniq', 'unique(trip_no, company_id)', 'Trip No is Unique!'),
    ]

    def create(self, cr, uid, vals, context=None):
        #if vals['business_trip'] == True:
        #    if vals.get('trip_no','/')=='/':
        #        vals['trip_no'] = self.pool.get('ir.sequence').get(cr, uid, 'hr.holidays') or '/'
        #    return super(hr_holidays, self).create(cr, uid, vals, context=context)    
        #else:
            return super(hr_holidays, self).create(cr, uid, vals, context=context)
                    

    #def generate_trip_number(self, cr, uid, vals, context=None):
        #if vals['business_trip'] == True:
        #    if vals.get('trip_no','/')=='/':
        #        vals['trip_no'] = self.pool.get('ir.sequence').get(cr, uid, 'hr.holidays') or '/'
    
    def send_trips_mail(self, cr, uid, ids, context=None):
        print "hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh"
        
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        #try:
        template_id = ir_model_data.get_object_reference(cr, uid, 'zeeva_hr', 'trips_send_email_template')[1]
        print template_id, "jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj"
        #except ValueError:
        #    template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict(context)
        ctx.update({
            'default_model': 'hr.holidays',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
        
    '''def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        print 'in the fields view get'
        if view_type == 'form': #and not view_id:
            mod_obj = self.pool.get('ir.model.data')
            if self._name == "hr.expense.expense":
                model, view_id = mod_obj.get_object_reference(cr, uid, 'hr_expenses_custom', 'view_expenses_form_inherit' )
                print model, view_id
            if self._name == "hr.holidays":
                model, view_id = mod_obj.get_object_reference(cr, uid, 'zeeva_hr' , 'edit_business_trips_new')
                print model, view_id
        return super(hr_holidays, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)'''

    def display_budget(self, cr, uid, ids, context=None):
        print "gggggggggggggggggggggggggggggggggggggggggggggggggg"
        for x in self.browse(cr, uid, ids, context=None):
            form_id = x.id
            emp_grade = x.employee_grade
            city = x.city.id
            city_classification_level = x.city.classification_level
            city_details = x.travelled_city_line_details
            
            if not city_details:
                raise osv.except_osv(_('Warning!'),_("Please mention the cities you will be travelling to during your trip"))
            print emp_grade, city_classification_level, "---------------------------------------------------------------"
            
            cr.execute('delete from gradewise_mode_of_travel_details_budget where travel_id=%s',([form_id]))
            
            cr.execute('delete from lodging_expenses_budget where lodging_expenses_id=%s',([form_id]))
            
            cr.execute('delete from boarding_expenses_budget where boarding_expenses_id=%s',([form_id]))
            
            search_emp_grade = self.pool.get('gradewise.mode.of.travel.details').search(cr, uid, [('grade', '=', emp_grade)])
            print search_emp_grade, "iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
            
            for m in self.pool.get('gradewise.mode.of.travel.details').browse(cr, uid, search_emp_grade):
                grade = m.grade
                sr_no = m.sr_no
                mode_of_travel = m.mode_of_travel
                mode_of_local_conveyance = m.mode_of_local_conveyance
                
                print grade, sr_no, mode_of_travel, mode_of_local_conveyance, "ttttttttttttttttttttttttttttttttttttttttttttttttttttttttt"
                
                create_id1 = self.pool.get('gradewise.mode.of.travel.details.budget').create(cr, uid, {'sr_no':1, 'grade':grade, 'mode_of_travel':mode_of_travel, 'mode_of_local_conveyance':mode_of_local_conveyance, 'travel_id':form_id}, context=context)
                
            search_city_details = self.pool.get('travelled.city.details').search(cr, uid, [('city_id', '=', form_id)])
            print search_city_details, "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
            
            sr_no = 0
            
            for k in self.pool.get('travelled.city.details').browse(cr, uid, search_city_details):
                #grade = m.grade
                city_name = k.city.id
                classification_level = k.city.classification_level
                print city_name, "tttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt"    
                sr_no = sr_no + 1
                search_travel_policies_rules = self.pool.get('travel.policies.rules').search(cr, uid, [('name', '=', 'Travel Policies/Eligibilities')])
                print search_travel_policies_rules, "mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm"
            
                search_travel_policies_lodging = self.pool.get('travel.policies.lodging').search(cr, uid, [('lodging_id', '=', search_travel_policies_rules[0]),('classification_level', '=', classification_level),('grade', '=', emp_grade)])
                print search_travel_policies_lodging, "nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn"
                
                
                for g in self.pool.get('travel.policies.lodging').browse(cr, uid, search_travel_policies_lodging):
                #grade = m.grade
                    classification_level = g.classification_level
                    min_expense = g.expense_low
                    max_expense = g.expense_high
                
                    create_id2 = self.pool.get('lodging.expenses.budget').create(cr, uid, {'sr_no':sr_no, 'city':city_name, 'classification_level':classification_level, 'expense_low':min_expense, 'expense_high':max_expense, 'lodging_expenses_id':form_id}, context=context)
                
                search_travel_policies_boarding = self.pool.get('travel.policies.boarding').search(cr, uid, [('boarding_id', '=', search_travel_policies_rules[0]),('classification_level', '=', classification_level),('grade', '=', emp_grade)])
                print search_travel_policies_boarding, "nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn"
            
                for j in self.pool.get('travel.policies.boarding').browse(cr, uid, search_travel_policies_boarding):
                #grade = m.grade
                    classification_level = j.classification_level
                    min_expense = j.expense_low
                    max_expense = j.expense_high
                
                    create_id3 = self.pool.get('boarding.expenses.budget').create(cr, uid, {'sr_no':sr_no, 'city':city_name, 'classification_level':classification_level, 'expense_low':min_expense, 'expense_high':max_expense, 'boarding_expenses_id':form_id}, context=context)
        #self.write(cr, uid, ids, {'state':'confirm'})
        
    def action_submit_business_trip_form(self, cr, uid, ids, context=None):
        print "gggggggggggggggggggggggggggggggggggggggggggggggggg"
        
        
        
        for h in self.browse(cr, uid, ids, context=None):
            gradewise_travel_details = h.gradewise_travel_details
        if not gradewise_travel_details:
            raise osv.except_osv(_('Warning!'),_("You need to display and view the budget before you submit the business trip. Please click on 'Display Budget'"))
            
        for m in self.browse(cr, uid, ids, context=None):
            planned_expense_line_details = m.planned_expense_line_details
        if not planned_expense_line_details:
            raise osv.except_osv(_('Warning!'),_("You need to mention the Planned Expenses for the business trip before submitting the trip"))
        
        
        search_lodging_expenses_budget_details = self.pool.get('lodging.expenses.budget').search(cr, uid, [('lodging_expenses_id', '=', ids[0])])
        print search_lodging_expenses_budget_details, "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        
        lodging_city = []
        for p in self.pool.get('lodging.expenses.budget').browse(cr, uid, search_lodging_expenses_budget_details):
            lodging_city_name = p.city.name
            lodging_classification_level = p.classification_level
            lodging_expense_low = p.expense_low
            lodging_expense_high = p.expense_high
            
            lodging_city.append(lodging_city_name)
            
            
            
            print lodging_city_name, lodging_classification_level, lodging_expense_low, lodging_expense_high, "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
        print lodging_city, "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
            
        search_boarding_expenses_budget_details = self.pool.get('boarding.expenses.budget').search(cr, uid, [('boarding_expenses_id', '=', ids[0])])
        print search_boarding_expenses_budget_details, "ccccccccccccccccccccccccccccccccccccccccccccccccccc"
        
        for q in self.pool.get('boarding.expenses.budget').browse(cr, uid, search_boarding_expenses_budget_details):
            boarding_city = q.city.name
            boarding_classification_level = q.classification_level
            boarding_expense_low = q.expense_low
            boarding_expense_high = q.expense_high
            
            print boarding_city, boarding_classification_level, boarding_expense_low, boarding_expense_high, "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
        
        
        for i in self.browse(cr, uid, ids, context=None):
            expense_date_from = i.date_from[:10]
            expense_date_to = i.date_to[:10]
            
        search_city_details = self.pool.get('travelled.city.details').search(cr, uid, [('city_id', '=', ids[0])])
        
        cities_list = []
        
        for n in self.pool.get('travelled.city.details').browse(cr, uid, search_city_details):
            city_name = n.city.name
            
            cities_list.append(city_name)
            
            print city_name, "llllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll"
        
        print cities_list, "+++++++++++++++++++++++++++++++ CITIES LIST ++++++++++++++++++++++++++++++++++++++++++"
        
        search_advance_amount_details = self.pool.get('advance.amount').search(cr, uid, [('advance_id', '=', ids[0])])
        
        count6=0
        
        for g in self.pool.get('advance.amount').browse(cr, uid, search_advance_amount_details):
            advance_date = g.date_of_advance
            
            count6 = count6+1
            
            if advance_date>expense_date_to:
                raise osv.except_osv(_('Warning!'),_("In 'Provision for Advance Amount' tab, in the record no. %s, the date of advance is incorrect. The Advance Amount has to be given to the Employee before the Trip gets over")%(count6))
        
        search_planned_expense_line_details = self.pool.get('planned.budget.expenses').search(cr, uid, [('planned_budget_id', '=', ids[0])])
        print search_planned_expense_line_details, "dddddddddddddddddddddddddddddddddddddddddddddddddd"
        
        count5=0
        
        for t in self.pool.get('planned.budget.expenses').browse(cr, uid, search_planned_expense_line_details):
            planned_description = t.description
            planned_city = t.city.name
            planned_type_of_stay = t.type_of_stay
            planned_total_amount = t.unit_amount
            planned_expense_date_from = t.expense_from
            planned_expense_date_to = t.expense_to
            print planned_description, planned_city, planned_type_of_stay, planned_total_amount, "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
            
            count5 = count5+1
            
            if planned_city not in cities_list:
                raise osv.except_osv(_('Warning!'),_("In Planned Expenses in the record no. %s, the city mentioned is not selected in the list of cities")%(count5))
            
            
            if not (planned_expense_date_from or planned_expense_date_to):
                raise osv.except_osv(_('Warning!'),_("In Planned Expenses in the record no. %s, please specify the from and to dates for the corresponding expense")%(count5))
            elif not (planned_expense_date_from>=expense_date_from and planned_expense_date_to<=expense_date_to):
                raise osv.except_osv(_('Warning!'),_("In Planned Expenses in the record no. %s, the dates specified do not lie in the range of trip duration")%(count5))
            
            if not planned_total_amount:
                raise osv.except_osv(_('Warning!'),_("In Planned Expenses in the record no. %s, please specify the amount for the corresponding expense")%(count5))
            
        for e in self.pool.get('lodging.expenses.budget').browse(cr, uid, search_lodging_expenses_budget_details):
            lodging_budget_city_name = e.city.name
            lodging_expense_low_value = e.expense_low
            lodging_expense_high_value = e.expense_high
            
            print "111111111111111111111111111111111111111111111111111111111111", lodging_budget_city_name, lodging_expense_low_value, lodging_expense_high_value
            
            count = 0
            
            for f in self.pool.get('planned.budget.expenses').browse(cr, uid, search_planned_expense_line_details):
                planned_expense_city = f.city.name
                planned_total_amount = f.unit_amount
                type_of_stay = f.type_of_stay
                count = count+1
                print "2222222222222222222222222222222222222222222222222222222222", planned_expense_city, planned_total_amount
                
                if planned_expense_city == lodging_budget_city_name and type_of_stay == 'Lodging':
                    if not (planned_total_amount<=lodging_expense_high_value):
                        raise osv.except_osv(_('Warning!'),_("In Planned Expenses in the record no. %s, the amount given %s for lodging in the city %s exceeds the budgetary range %s to %s")%(count,planned_total_amount,planned_expense_city,lodging_expense_low_value,lodging_expense_high_value))
                        
        for g in self.pool.get('boarding.expenses.budget').browse(cr, uid, search_boarding_expenses_budget_details):
            boarding_budget_city_name = g.city.name
            boarding_expense_low_value = g.expense_low
            boarding_expense_high_value = g.expense_high
            
            print "111111111111111111111111111111111111111111111111111111111111", boarding_budget_city_name, boarding_expense_low_value, boarding_expense_high_value
            
            count = 0
            
            for h in self.pool.get('planned.budget.expenses').browse(cr, uid, search_planned_expense_line_details):
                planned_expense_city_boarding = h.city.name
                planned_total_amount_boarding = h.unit_amount
                type_of_stay_boarding = h.type_of_stay
                count = count+1
                print "2222222222222222222222222222222222222222222222222222222222", planned_expense_city_boarding, planned_total_amount_boarding
                
                if planned_expense_city_boarding == boarding_budget_city_name and type_of_stay_boarding == 'Boarding':
                    if not (planned_total_amount_boarding<=boarding_expense_high_value):
                        raise osv.except_osv(_('Warning!'),_("In Planned Expenses in the record no. %s, the amount given %s for boarding in the city %s exceeds the budgetary range %s to %s")%(count,planned_total_amount_boarding,planned_expense_city_boarding,boarding_expense_low_value,boarding_expense_high_value))                
        
        for e in self.browse(cr, uid, ids, context=None):
            trip_no = e.trip_no
            business_trip = e.business_trip
            hro_work_email = e.employee_id.hro.email
            manager_work_email = e.employee_id.parent_id.work_email
            
            print hro_work_email, manager_work_email, "pppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp"
            
            search_sequence_record = self.pool.get('ir.sequence').search(cr,uid,[('code','=','hr.holidays')], context=context)            
            print search_sequence_record, "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"
            
            #write_sequence_code = self.pool.get('ir.sequence').write(cr, uid, search_sequence_record, {'prefix': dept_code})
            
            for j in self.pool.get('ir.sequence').browse(cr, uid, search_sequence_record):
                prefix = j.prefix
                prefix_string = str(prefix)
                print prefix, type(prefix), prefix_string, type(prefix_string),"lllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll"
                
                trip_sequence_no = self.pool.get('ir.sequence').get(cr, uid, 'hr.holidays') or '/'
                
                print trip_sequence_no, type(trip_sequence_no), "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
                
                sequence_number_of_trip = trip_sequence_no
            
            self.write(cr, uid, ids, {'trip_no':sequence_number_of_trip}) 
            
            search_trip_submit_email_template = self.pool.get('email.template').search(cr,uid,[('model_id.model','=','hr.holidays'),('lang','=','trip submit')], context=context)
            
            if search_trip_submit_email_template and business_trip == True:
            
                #send_trip_submit_mail = self.pool.get('email.template').send_mail(cr, uid, search_trip_submit_email_template[0], ids[0], force_send=True, context=context)
                print "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            subscribe_ids = []
            
            if e.employee_id and e.employee_id.parent_id and e.employee_id.parent_id.user_id:
                subscribe_ids = [e.employee_id.parent_id.user_id.id,e.employee_id.hro.id,58,59,64]   
            subscribe_ids.append(e.employee_id.user_id.id) #related employee added to the follower list
            
            self.message_subscribe_users(cr, SUPERUSER_ID, [e.id], user_ids=subscribe_ids, context=context)	                
        self.write(cr, uid, ids, {'state':'confirm'})
        
    #def onchange_employee(self, cr, uid, ids, employee_id):
    #    values = {}
    #    print "tttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt"
    #    result = {'value': {'department_id': False, 'employee_grade': False}}
    #    if employee_id:
    #        print employee.department_id.id, employee.employee_grade.id, "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
    #        employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
    #        result['value'] = {'department_id': employee.department_id.id, 'employee_grade': employee.employee_grade.id}
    #    return result      

    def holidays_refuse(self, cr, uid, ids, context=None):
        
        for x in self.browse(cr, uid, ids, context=None):
            specify_reason_for_refusal = x.specify_reason_for_refusal 
            leave_record_type = x.type
            reason_for_refusal = x.reason_for_refusal
            hro_user_id = x.employee_id.hro.id
            employee_id = x.employee_id.id
            business_trip = x.business_trip
            search_user_ids = self.pool.get('res.users').search(cr,uid,[('name','in',('Prakash Butani','Nitin Butani','Akshay Butani'))], context=context)
            if uid not in search_user_ids:
                if x.employee_id.user_id.id == uid:
                    if business_trip:
                        raise osv.except_osv(_('Warning!'),_('You cannot Refuse your own Business Trip '))
                    else:
                        raise osv.except_osv(_('Warning!'),_('You cannot Refuse your own Leave Request '))
            
        
        #if uid == hro_user_id:
         #   raise osv.except_osv(_('Warning!'),_("You cannot refuse a Business Trip"))     
        
        
        if leave_record_type == 'add':
            print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
            obj_emp = self.pool.get('hr.employee')
            ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
            manager = ids2 and ids2[0] or False
            for holiday in self.browse(cr, uid, ids, context=context):
                if holiday.state == 'validate1':
                    self.write(cr, uid, [holiday.id], {'state': 'refuse', 'manager_id': manager})
                else:
                    self.write(cr, uid, [holiday.id], {'state': 'refuse', 'manager_id2': manager})
        
        
        
        
        
        if specify_reason_for_refusal == False and leave_record_type == 'remove':
            raise osv.except_osv(_('Warning!'),_("Please specify a reason for refusal. Click on the checkbox for 'Specify reason for refusal'"))
            
        elif specify_reason_for_refusal == True:
            if not reason_for_refusal:
                raise osv.except_osv(_('Warning!'),_("Please specify a reason for refusal"))     
        
            else:

                obj_emp = self.pool.get('hr.employee')
                ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
                manager = ids2 and ids2[0] or False
                for holiday in self.browse(cr, uid, ids, context=context):
                    if holiday.state == 'validate1':
                        self.write(cr, uid, [holiday.id], {'state': 'refuse', 'manager_id': manager})
                    else:
                        self.write(cr, uid, [holiday.id], {'state': 'refuse', 'manager_id2': manager})

            #search_template = self.pool.get('email.template').search(cr,uid,[('model_id.model','=','hr.holidays')], context=context)
            
            
            for x in self.browse(cr, uid, ids, context=None):
                leave_type = x.holiday_status_id.id
                leave_type_name = x.holiday_status_id.name
                employee_id = x.employee_id.id
                number_of_days = x.number_of_days_temp
                holidays_type = x.type
                double_validation = x.holiday_status_id.double_validation
                privilege_leaves = x.remaining_privilege_leaves
                business_trip = x.business_trip
                trip_state = x.state
            

            search_emp_record = self.pool.get('hr.employee').search(cr,uid,[('id','=',employee_id)], context=context)
            
            for h in self.pool.get('hr.employee').browse(cr,uid,search_emp_record):
                sick_leaves = h.sick_leaves
                total_sick_leaves_allocated = sick_leaves - number_of_days
                total_sick_leaves_deducted = sick_leaves + number_of_days
                
                casual_leaves = h.casual_leaves
                total_casual_leaves_allocated = casual_leaves - number_of_days
                total_casual_leaves_deducted = casual_leaves + number_of_days

                compensatory_leaves = h.compensatory_leaves
                total_compensatory_leaves_allocated = compensatory_leaves - number_of_days
                total_compensatory_leaves_deducted = compensatory_leaves + number_of_days
                
                total_privilege_leaves_allocated = privilege_leaves - number_of_days
                total_privilege_leaves_deducted = privilege_leaves + number_of_days
                
            
            if holidays_type == 'add' and leave_type_name == 'Sick Leave (SL)':
                
                sick_leave_allocated_write_id = self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'sick_leaves': total_sick_leaves_allocated})
                sick_leave_allocated_write_id_on_leaves_form = self.write(cr, uid, ids, {'remaining_sick_leaves': total_sick_leaves_allocated})

            elif holidays_type == 'remove' and leave_type_name == 'Sick Leave (SL)':
                
                sick_leave_request_write_id = self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'sick_leaves': total_sick_leaves_deducted})
                sick_leave_requested_write_id_on_leaves_form = self.write(cr, uid, ids, {'remaining_sick_leaves': total_sick_leaves_deducted})

            elif holidays_type == 'add' and leave_type_name == 'Casual Leave (CL)':
                
                casual_leave_allocated_write_id = self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'casual_leaves': total_casual_leaves_allocated})
                casual_leave_allocated_write_id_on_leaves_form = self.write(cr, uid, ids, {'remaining_casual_leaves': total_casual_leaves_allocated})

            elif holidays_type == 'remove' and leave_type_name == 'Casual Leave (CL)':
                
                casual_leave_request_write_id = self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'casual_leaves': total_casual_leaves_deducted})
                casual_leave_request_write_id_on_leaves_form = self.write(cr, uid, ids, {'remaining_casual_leaves': total_casual_leaves_deducted})

            elif holidays_type == 'add' and leave_type_name == 'Compensatory-Off (CO)':
                
                compensatory_leave_allocated_write_id = self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'compensatory_leaves': total_compensatory_leaves_allocated})
                compensatory_leave_allocated_write_id_on_leaves_form = self.write(cr, uid, ids, {'remaining_compensatory_leaves': total_compensatory_leaves_allocated})

            elif holidays_type == 'remove' and leave_type_name == 'Compensatory-Off (CO)':
                
                compensatory_leave_request_write_id = self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'compensatory_leaves': total_compensatory_leaves_deducted})
                compensatory_leave_request_write_id_on_leaves_form = self.write(cr, uid, ids, {'remaining_compensatory_leaves': total_compensatory_leaves_deducted})
                
            elif holidays_type == 'add' and leave_type_name == 'Privilege Leave (PL)':
                
                #compensatory_leave_allocated_write_id = self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'compensatory_leaves': total_compensatory_leaves_allocated})
                privilege_leave_allocated_write_id_on_leaves_form = self.write(cr, uid, ids, {'remaining_privilege_leaves': total_privilege_leaves_allocated})

            elif holidays_type == 'remove' and leave_type_name == 'Privilege Leave (PL)':
                
                #compensatory_leave_request_write_id = self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'compensatory_leaves': total_compensatory_leaves_deducted})
                privilege_leave_request_write_id_on_leaves_form = self.write(cr, uid, ids, {'remaining_privilege_leaves': total_privilege_leaves_deducted})

            #if search_template:
            
            #    send_leave_request_mail = self.pool.get('email.template').send_mail(cr, uid, search_template[0], ids[0], force_send=True, context=context)
            
            if business_trip == True:
                print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                if holiday.state == 'confirm':
                    print "-------------------------------------------------------------------------"
                    search_trip_refuse_by_HRO_email_template = self.pool.get('email.template').search(cr,uid,[('model_id.model','=','hr.holidays'),('lang','=','trip refuse by HRO')], context=context)
                    
                    print search_trip_refuse_by_HRO_email_template, "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
            
                    #if search_trip_refuse_by_HRO_email_template: 
            
                    #    send_trip_refuse_by_HRO_email = self.pool.get('email.template').send_mail(cr, uid, search_trip_refuse_by_HRO_email_template[0], ids[0], force_send=True, context=context)
                        
                elif holiday.state == 'validate1' or holiday.state == 'validate':
                        
                    search_trip_refuse_by_Mgmt_email_template = self.pool.get('email.template').search(cr,uid,[('model_id.model','=','hr.holidays'),('lang','=','trip refuse by Mgmt')], context=context)
            
                    #if search_trip_refuse_by_Mgmt_email_template: 
            
                    #    send_trip_refuse_by_Mgmt_email = self.pool.get('email.template').send_mail(cr, uid, search_trip_refuse_by_Mgmt_email_template[0], ids[0], force_send=True, context=context)    
                        
            elif business_trip == False:
                print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                if holiday.state == 'confirm':
                    print "-------------------------------------------------------------------------"
                    search_leave_refuse_by_HRO_email_template = self.pool.get('email.template').search(cr,uid,[('model_id.model','=','hr.holidays'),('lang','=','leave refuse by HRO')], context=context)
                    
                    print search_leave_refuse_by_HRO_email_template, "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
            
                    if search_leave_refuse_by_HRO_email_template: 
            
                        #send_leave_refuse_by_HRO_email = self.pool.get('email.template').send_mail(cr, uid, search_leave_refuse_by_HRO_email_template[0], ids[0], force_send=True, context=context)
                        print "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
                        
                elif holiday.state == 'validate1' or holiday.state == 'validate':
                        
                    search_leave_refuse_by_Mgmt_email_template = self.pool.get('email.template').search(cr,uid,[('model_id.model','=','hr.holidays'),('lang','=','leave refuse by Mgmt')], context=context)
            
                    if search_leave_refuse_by_Mgmt_email_template: 
            
                        #send_leave_refuse_by_Mgmt_email = self.pool.get('email.template').send_mail(cr, uid, search_leave_refuse_by_Mgmt_email_template[0], ids[0], force_send=True, context=context)   
                        print "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee" 
            message = _("Request Refused")
            self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)    
            self.holidays_cancel(cr, uid, ids, context=context)
            
            
                
        return True

    def holidays_cancel(self, cr, uid, ids, context=None):
        
        meeting_obj = self.pool.get('crm.meeting')
        for x in self.browse(cr, uid, ids, context=None):
            specify_reason_for_refusal = x.specify_reason_for_refusal   
            leave_record_type = x.type            
        if specify_reason_for_refusal == False and leave_record_type == 'remove':
            raise osv.except_osv(_('Warning!'),_("Please specify a reason for refusal. Click on the checkbox for 'Specify reason for refusal'"))
        else:
            for record in self.browse(cr, uid, ids):
            # Delete the meeting
                if record.meeting_id:
                    meeting_obj.unlink(cr, uid, [record.meeting_id.id])

            # If a category that created several holidays, cancel all related
                wf_service = netsvc.LocalService("workflow")
                for request in record.linked_request_ids or []:
                    wf_service.trg_validate(uid, 'hr.holidays', request.id, 'refuse', cr)

        

            self._remove_resource_leave(cr, uid, ids, context=context)
        return True
        
    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            search_hro = self.pool.get('res.users').search(cr, uid, [('is_hro', '=', True)])
            print uid, search_hro, "lllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll"
            
            #search_accounts_officers = self.pool.get('hr.employee').search(cr, uid, [('department', '=', True)])
            search_accounts_department = self.pool.get('hr.department').search(cr, uid, [('name', '=',  'Accounts & Finance')])
            search_accounts_officers = self.pool.get('hr.employee').search(cr, uid, [('department_id', '=', search_accounts_department[0])])
            
            for y in self.pool.get('hr.employee').browse(cr,uid,search_accounts_officers):
                accounts_user_id = y.user_id.id
                print accounts_user_id, "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
                
                if uid==accounts_user_id and rec.employee_id.user_id.id!=uid:
                   raise osv.except_osv(_('Warning!'),_('You cannot delete a business trip'))
                   
            print search_accounts_department, search_accounts_officers, "gggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg"
            
            
            
            if uid in search_hro and rec.business_trip==True and rec.employee_id.user_id.id!=uid:
                raise osv.except_osv(_('Warning!'),_('You cannot delete a business trip'))
                
            #if rec.employee_id.job_id.name in ['Accounts Executive','Senior Accountant']:    
            #    raise osv.except_osv(_('Warning!'),_('You cannot delete a business trip'))
                
            if rec.state not in ['draft', 'cancel', 'confirm'] and rec.business_trip==True:
                raise osv.except_osv(_('Warning!'),_('You cannot delete a trip which is in %s state.')%(rec.state))
                
            elif rec.state not in ['draft', 'cancel', 'confirm'] and rec.business_trip==False:
                raise osv.except_osv(_('Warning!'),_('You cannot delete a leave which is in %s state.')%(rec.state))
                
            
        return super(hr_holidays, self).unlink(cr, uid, ids, context)    

    def holidays_first_validate(self, cr, uid, ids, context=None):
        
        
        self.check_holidays(cr, uid, ids, context=context)
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        self.holidays_first_validate_notificate(cr, uid, ids, context=context)

        
        for x in self.browse(cr, uid, ids, context=None):
            leave_type = x.holiday_status_id.id
            leave_type_name = x.holiday_status_id.name
            employee_id = x.employee_id.id
            number_of_days = x.number_of_days_temp
            holidays_type = x.type
            double_validation = x.holiday_status_id.double_validation
            business_trip = x.business_trip
            hro_user_id = x.employee_id.hro.id
            
            #if uid == hro_user_id:
             #  raise osv.except_osv(_('Warning!'),_('You cannot approve a Business Trip'))    
            search_user_ids = self.pool.get('res.users').search(cr,uid,[('name','in',('Prakash Butani','Nitin Butani','Akshay Butani'))], context=context)
            if uid not in search_user_ids:
                if x.employee_id.user_id.id == uid:
                    if business_trip:
                        raise osv.except_osv(_('Warning!'),_('You cannot Approve your own Business Trip '))
                    else:
                        raise osv.except_osv(_('Warning!'),_('You cannot Approve your own Leave Request '))
            search_emp_record = self.pool.get('hr.employee').search(cr,uid,[('id','=',employee_id)], context=context)
            
            for h in self.pool.get('hr.employee').browse(cr,uid,search_emp_record):
                sick_leaves = h.sick_leaves
                total_sick_leaves_allocated = sick_leaves + number_of_days
                total_sick_leaves_deducted = sick_leaves - number_of_days
                
                casual_leaves = h.casual_leaves
                total_casual_leaves_allocated = casual_leaves + number_of_days
                total_casual_leaves_deducted = casual_leaves - number_of_days

                compensatory_leaves = h.compensatory_leaves
                total_compensatory_leaves_allocated = compensatory_leaves + number_of_days
                total_compensatory_leaves_deducted = compensatory_leaves - number_of_days
                
            if double_validation == False:
              
              if holidays_type == 'add' and leave_type_name == 'Sick Leave (SL)':
                
                sick_leave_allocated_write_id = self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'sick_leaves': total_sick_leaves_allocated})

              elif holidays_type == 'remove' and leave_type_name == 'Sick Leave (SL)':
                
                sick_leave_request_write_id = self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'sick_leaves': total_sick_leaves_deducted})

              elif holidays_type == 'add' and leave_type_name == 'Casual Leave (CL)':
                
                casual_leave_allocated_write_id = self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'casual_leaves': total_casual_leaves_allocated})

              elif holidays_type == 'remove' and leave_type_name == 'Casual Leave (CL)':
                
                casual_leave_request_write_id = self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'casual_leaves': total_casual_leaves_deducted})

              elif holidays_type == 'add' and leave_type_name == 'Compensatory-Off (CO)':
                
                compensatory_leave_allocated_write_id = self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'compensatory_leaves': total_compensatory_leaves_allocated})

              elif holidays_type == 'remove' and leave_type_name == 'Compensatory-Off (CO)':
                
                compensatory_leave_request_write_id = self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'compensatory_leaves': total_compensatory_leaves_deducted})
                
            search_trip_validate_by_HR_email_template = self.pool.get('email.template').search(cr,uid,[('model_id.model','=','hr.holidays'),('lang','=','trip approve by HR')], context=context)
            
            #if search_trip_validate_by_HR_email_template and business_trip == True:
            
            #    send_trip_validate_by_HR_mail = self.pool.get('email.template').send_mail(cr, uid, search_trip_validate_by_HR_email_template[0], ids[0], force_send=True, context=context)    

        return self.write(cr, uid, ids, {'state':'validate1', 'manager_id': manager})



    def holidays_validate(self, cr, uid, ids, context=None):
        
        
        self.check_holidays(cr, uid, ids, context=context)
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        self.write(cr, uid, ids, {'state':'validate'})
        data_holiday = self.browse(cr, uid, ids)
        for record in data_holiday:
            self.write(cr, uid, ids, {'current_user':uid})
            if record.double_validation:
                self.write(cr, uid, [record.id], {'manager_id2': manager})
            else:
                self.write(cr, uid, [record.id], {'manager_id': manager})
            if record.holiday_type == 'employee' and record.type == 'remove':
                meeting_obj = self.pool.get('crm.meeting')
                meeting_vals = {
                    'name': record.name or _('Leave Request'),
                    'categ_ids': record.holiday_status_id.categ_id and [(6,0,[record.holiday_status_id.categ_id.id])] or [],
                    'duration': record.number_of_days_temp * 8,
                    'description': record.notes,
                    'user_id': record.user_id.id,
                    'date': record.date_from,
                    'end_date': record.date_to,
                    'date_deadline': record.date_to,
                    'state': 'open',            # to block that meeting date in the calendar
                }
                meeting_id = meeting_obj.create(cr, uid, meeting_vals)
                self._create_resource_leave(cr, uid, [record], context=context)
                self.write(cr, uid, ids, {'meeting_id': meeting_id})
            elif record.holiday_type == 'category':
                emp_ids = obj_emp.search(cr, uid, [('category_ids', 'child_of', [record.category_id.id])])
                leave_ids = []
                for emp in obj_emp.browse(cr, uid, emp_ids):
                    vals = {
                        'name': record.name,
                        'type': record.type,
                        'holiday_type': 'employee',
                        'holiday_status_id': record.holiday_status_id.id,
                        'date_from': record.date_from,
                        'date_to': record.date_to,
                        'notes': record.notes,
                        'number_of_days_temp': record.number_of_days_temp,
                        'parent_id': record.id,
                        'employee_id': emp.id
                    }
                    leave_ids.append(self.create(cr, uid, vals, context=None))
                wf_service = netsvc.LocalService("workflow")
                for leave_id in leave_ids:
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'confirm', cr)
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'validate', cr)
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'second_validate', cr)

        
        for x in self.browse(cr, uid, ids, context=None):
            leave_type = x.holiday_status_id.id
            leave_type_name = x.holiday_status_id.name
            employee_id = x.employee_id.id
            number_of_days = x.number_of_days_temp
            holidays_type = x.type
            double_validation = x.holiday_status_id.double_validation
            privilege_leaves = x.remaining_privilege_leaves
            business_trip = x.business_trip
            
            search_user_ids = self.pool.get('res.users').search(cr,uid,[('name','in',('Prakash Butani','Nitin Butani','Akshay Butani'))], context=context)
            if uid not in search_user_ids:
                if x.employee_id.user_id.id == uid:
                    if business_trip:
                        raise osv.except_osv(_('Warning!'),_('You cannot Approve your own Business Trip '))
                    else:
                        raise osv.except_osv(_('Warning!'),_('You cannot Approve your own Leave Request '))
            
            date_from = x.date_from
            date_to = x.date_to
            date_against_which_CO_taken = x.date_against_which_CO_taken
            compensatory_expiry_date = x.compensatory_expiry_date
            
            search_compensatory_leaves = self.pool.get('compensatory.leaves.table').search(cr,uid,[('compensatory_id','=',ids[0])], context=context)
            
            print search_compensatory_leaves, "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
            
            if x.business_trip == True:
                date_from_year = int(date_from[:4])
                date_from_month = int(date_from[5:7])
                date_from_date = int(date_from[8:10])

                date_to_year = int(date_to[:4])
                date_to_month = int(date_to[5:7])
                date_to_date = int(date_to[8:10])
                
                weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

                from datetime import date, timedelta as td

                d1 = date(date_from_year,date_from_month,date_from_date)
                d2 = date(date_to_year,date_to_month,date_to_date)

                print d1,d2, "-------------------------------- DATE FROM DATE TO--------------------------------------"

                delta = d2 - d1

                count = 0.0
                
                cr.execute('delete from compensatory_leaves_trips where compensatory_trip_id=%s and trip_no=%s',(x.employee_id.id,x.id))
                
                for i in range(delta.days + 1):
                       date_in_list =  d1 + td(days=i)
                       
                       print date_in_list, "-----------------------DATE IN LIST-------------------------------------"
            
            
                       week_number_list = datetime.datetime(date_in_list.year, date_in_list.month, date_in_list.day).weekday()
            
                       print week_number_list, "------------------------WEEK NUMBER LIST---------------------------------------------"
                       
                       if (weekdays[week_number_list] == 'Saturday' or weekdays[week_number_list] == 'Sunday'):
                                print date_in_list, x.employee_id.name, "ZZZZZZZZZZZZZZZZZZZZZZZZZZ DATE IN LIST FOR SATURDAY OR SUNDAY ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ"
                                
                                count = count+1.0    
                                
                                search_emp_id = self.pool.get('hr.employee').search(cr,uid,[('id','=',x.employee_id.id)], context=context) 
                                
                                search_compensatory_leave = self.pool.get('hr.holidays.status').search(cr,uid,[('name','=','Compensatory-Off (CO)')], context=context)
                                
                                create_comp_trip_id = self.pool.get('compensatory.leaves.trips').create(cr, uid, {'serial_no': count,'trip_no': x.id, 'number_of_compensatory_offs': 1, 'compensatory_date':date_in_list,'day_of_week': str(week_number_list), 'compensatory_trip_id': search_emp_id[0]}, context=context)
                                
                                create_allocation_id = self.pool.get('hr.holidays').create(cr, uid, {'name': 'Allocation of 1 CO', 'holiday_status_id': search_compensatory_leave[0], 'employee_id': x.employee_id.id, 'number_of_days_temp': 1, 'type': 'add'}, context=context)
               
               
                                #self.pool.get('hr.holidays').holidays_first_validate(cr, uid, [create_allocation_id], context=context)
                                self.pool.get('hr.holidays').holidays_validate(cr, uid, [create_allocation_id], context=context) 
                                
                                #for t in self.pool.get('hr.employee').browse(cr, uid, search_emp_id):                               
                                #        compensatory_leaves = t.compensatory_leaves
                                #        compensatory_leaves = compensatory_leaves+1
                                        
                                #        compensatory_leave_allocated = self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'sick_leaves': total_sick_leaves_allocated})
                                        
                                #        print compensatory_leaves, "---------------------- COMPENSATORY LEAVES ------------------------------"  
                                

            if holidays_type == 'remove' and leave_type_name == 'Compensatory-Off (CO)':
                for k in self.pool.get('compensatory.leaves.table').browse(cr, uid, search_compensatory_leaves):
                    compensatory_date_from = k.compensatory_date
                    compensatory_expiry_date = k.compensatory_expiry_date
                    date_against_which_CO_taken =k.date_against_which_CO_taken 
                    serial_no = k.serial_no   
                    create_co_id = self.pool.get('compensatory.leaves').create(cr, uid, {'serial_no': serial_no,'compensatory_date': compensatory_date_from, 'compensatory_expiry_date': compensatory_expiry_date, 'date_against_which_co_taken':date_against_which_CO_taken, 'compensatory_id': employee_id}, context=context)
            

            search_emp_record = self.pool.get('hr.employee').search(cr,uid,[('id','=',employee_id)], context=context)
            
            for h in self.pool.get('hr.employee').browse(cr,uid,search_emp_record):
                sick_leaves = h.sick_leaves
                total_sick_leaves_allocated = sick_leaves + number_of_days
                total_sick_leaves_deducted = sick_leaves - number_of_days
                
                casual_leaves = h.casual_leaves
                total_casual_leaves_allocated = casual_leaves + number_of_days
                total_casual_leaves_deducted = casual_leaves - number_of_days

                compensatory_leaves = h.compensatory_leaves
                total_compensatory_leaves_allocated = compensatory_leaves + number_of_days
                total_compensatory_leaves_deducted = compensatory_leaves - number_of_days
                
                total_privilege_leaves_allocated = privilege_leaves + number_of_days
                total_privilege_leaves_deducted = privilege_leaves - number_of_days

                
            
            if holidays_type == 'add' and leave_type_name == 'Sick Leave (SL)':
                
                sick_leave_allocated_write_id = self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'sick_leaves': total_sick_leaves_allocated})
                sick_leave_allocated_write_id_on_leaves_form = self.write(cr, uid, ids, {'remaining_sick_leaves': total_sick_leaves_allocated})

            elif holidays_type == 'remove' and leave_type_name == 'Sick Leave (SL)':
                
                sick_leave_request_write_id = self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'sick_leaves': total_sick_leaves_deducted})
                sick_leave_requested_write_id_on_leaves_form = self.write(cr, uid, ids, {'remaining_sick_leaves': total_sick_leaves_deducted})

            elif holidays_type == 'add' and leave_type_name == 'Casual Leave (CL)':
                
                casual_leave_allocated_write_id = self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'casual_leaves': total_casual_leaves_allocated})
                casual_leave_allocated_write_id_on_leaves_form = self.write(cr, uid, ids, {'remaining_casual_leaves': total_casual_leaves_allocated})

            elif holidays_type == 'remove' and leave_type_name == 'Casual Leave (CL)':
                
                casual_leave_request_write_id = self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'casual_leaves': total_casual_leaves_deducted})
                casual_leave_request_write_id_on_leaves_form = self.write(cr, uid, ids, {'remaining_casual_leaves': total_casual_leaves_deducted})

            elif holidays_type == 'add' and leave_type_name == 'Compensatory-Off (CO)':
                
                compensatory_leave_allocated_write_id = self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'compensatory_leaves': total_compensatory_leaves_allocated})
                compensatory_leave_allocated_write_id_on_leaves_form = self.write(cr, uid, ids, {'remaining_compensatory_leaves': total_compensatory_leaves_allocated})

            elif holidays_type == 'remove' and leave_type_name == 'Compensatory-Off (CO)':
                
                compensatory_leave_request_write_id = self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'compensatory_leaves': total_compensatory_leaves_deducted})
                compensatory_leave_request_write_id_on_leaves_form = self.write(cr, uid, ids, {'remaining_compensatory_leaves': total_compensatory_leaves_deducted})

            elif holidays_type == 'add' and leave_type_name == 'Privilege Leave (PL)':
                
                #compensatory_leave_allocated_write_id = self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'compensatory_leaves': total_compensatory_leaves_allocated})
                privilege_leave_allocated_write_id_on_leaves_form = self.write(cr, uid, ids, {'remaining_privilege_leaves': total_privilege_leaves_allocated})

            elif holidays_type == 'remove' and leave_type_name == 'Privilege Leave (PL)':
                
                #compensatory_leave_request_write_id = self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'compensatory_leaves': total_compensatory_leaves_deducted})
                privilege_leave_request_write_id_on_leaves_form = self.write(cr, uid, ids, {'remaining_privilege_leaves': total_privilege_leaves_deducted})
                
            search_trip_validate_by_Mgmt_email_template = self.pool.get('email.template').search(cr,uid,[('model_id.model','=','hr.holidays'),('lang','=','trip approve by Mgmt')], context=context)
            
            #if search_trip_validate_by_Mgmt_email_template and business_trip == True:
            
            #    send_trip_validate_by_Mgmt_mail = self.pool.get('email.template').send_mail(cr, uid, search_trip_validate_by_Mgmt_email_template[0], ids[0], force_send=True, context=context)        

        return True

        

    def onchange_employee(self, cr, uid, ids, employee_id):
        result = {'value': {'department_id': False}}
        if employee_id:
            employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            
            values = {
                'employee_grade': employee.employee_grade,
                'department_id' : employee.department_id.id,
                'remaining_privilege_leaves' : employee.remaining_leaves,
                'remaining_casual_leaves' : employee.casual_leaves,
                'remaining_sick_leaves' : employee.sick_leaves,
                'remaining_compensatory_leaves' : employee.compensatory_leaves,
                    }

        return {'value' : values}

    def onchange_date_against_which_CO_taken(self, cr, uid, ids, date_against_which_CO_taken):
        
        if date_against_which_CO_taken:
            
            

            co_date_year = int(date_against_which_CO_taken[:4])
            co_date_month = int(date_against_which_CO_taken[5:7])
            co_date_date = int(date_against_which_CO_taken[8:10])

            

            from dateutil.relativedelta import relativedelta

            import datetime
            from datetime import datetime
            from datetime import timedelta
            from time import strftime
            from datetime import date

            date_after_2months_from_co_date = date(co_date_year,co_date_month,co_date_date) + relativedelta(months=+2)
            values = {
                   'compensatory_expiry_date' : str(date_after_2months_from_co_date),
                    }

        return {'value' : values}

        


    def on_change_holiday_status_id(self, cr, uid, ids, holiday_status_id, context=None):
        values = {}
        if holiday_status_id:
            
            
            search_sick_leave = self.pool.get('hr.holidays.status').search(cr,uid,[('name','=','Sick Leave (SL)')], context=context)

            search_wedding_leave = self.pool.get('hr.holidays.status').search(cr,uid,[('name','=','Wedding Leave (WL)')], context=context)

            search_maternity_leave = self.pool.get('hr.holidays.status').search(cr,uid,[('name','=','Maternity Leave (ML)')], context=context)

            search_compensatory_leave = self.pool.get('hr.holidays.status').search(cr,uid,[('name','=','Compensatory-Off (CO)')], context=context)
            
            search_short_duration_business_trip = self.pool.get('hr.holidays.status').search(cr,uid,[('name','=','Short Duration Business Trip')], context=context)
            
            search_long_duration_business_trip = self.pool.get('hr.holidays.status').search(cr,uid,[('name','=','Long Duration Business Trip')], context=context)
            
            if holiday_status_id == search_short_duration_business_trip[0] or holiday_status_id == search_long_duration_business_trip[0]:
                
                
                values = {
                'business_trip':True,
                'upload_medical_certificate': False,
                'upload_wedding_card': False,
                'show_remaining_leaves': False,
                'upload_maternity_certificate':False,
                'compensatory_dates_boolean':False,
                    }
            
            elif holiday_status_id == search_sick_leave[0]:
                

                 values = {
                'business_trip':False,
                'upload_medical_certificate': True,
                'upload_wedding_card': False,
                'show_remaining_leaves': True,
                'upload_maternity_certificate':False,
                'compensatory_dates_boolean':False,
                    }

            elif holiday_status_id == search_compensatory_leave[0]:
                

                 values = {
                'business_trip':False,
                'upload_wedding_card': False,
                'upload_medical_certificate': False,
                'show_remaining_leaves': True,
                'upload_maternity_certificate':False,
                'compensatory_dates_boolean':True,
                    }
            
            elif holiday_status_id == search_wedding_leave[0]:
                

                 values = {
                'business_trip':False,
                'upload_wedding_card': True,
                'upload_medical_certificate': False,
                'show_remaining_leaves': True,
                'upload_maternity_certificate':False,
                'compensatory_dates_boolean':False,
                    }

            elif holiday_status_id == search_maternity_leave[0]:
                

                 values = {
                'business_trip':False,
                'upload_wedding_card': False,
                'upload_medical_certificate': False,
                'show_remaining_leaves': True,
                'upload_maternity_certificate':True,
                'compensatory_dates_boolean':False,
                    }
            
            else:

                values = {
                'business_trip':False,
                'upload_medical_certificate': False,
                'upload_wedding_card': False,
                'show_remaining_leaves': True,
                'upload_maternity_certificate':False,
                'compensatory_dates_boolean':False,
                    }
            
        return {'value' : values}
        

    def allocate_privilege_leaves_after_probation_period_completion(self, cr, uid, ids=None, context=None):
        emp_search = self.pool.get('hr.employee').search(cr, uid, [('id', '>', 0)], context=context)
        print emp_search, "------------------LIST OF EMPLOYEES--------------------------------------"
        for record in self.pool.get('hr.employee').browse(cr, uid, emp_search):

            

            joining_date = record.join_date
            emp_record_id = record.id
            
            print emp_record_id, joining_date, "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"

            remaining_leaves = record.remaining_leaves
            

            joining_date_year = int(joining_date[:4])
            joining_date_month = int(joining_date[5:7])
            joining_date_date = int(joining_date[8:10])
            print joining_date_year, joining_date_month, joining_date_date, "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
            from dateutil.relativedelta import relativedelta

            import datetime
            from datetime import datetime
            from datetime import timedelta
            from time import strftime
            from datetime import date

            if joining_date:
                date_dt= datetime.strptime(joining_date, "%Y-%m-%d").date()
                today = datetime.today().date()
                tenure = relativedelta(today, date_dt)

            no_of_years = tenure.years
            

            #Getting the date after 3 and 8 months from the date of joining

            date_after_3months = date(joining_date_year,joining_date_month,joining_date_date) + relativedelta(months=+3)
            date_after_8months = date(joining_date_year,joining_date_month,joining_date_date) + relativedelta(months=+8)

            search_privilege_leave = self.pool.get('hr.holidays.status').search(cr,uid,[('name','=','Privilege Leave (PL)')], context=context)

            from time import strftime
            today_date = strftime("%Y-%m-%d")
            
            ## Allocation of 5 Privilege Leaves on the date of completion of Probationary Period (i.e. at the end of 8 months from DOJ) --> after confirmation of an employee

            if today_date == str(date_after_3months):
               
               create_id = self.pool.get('hr.holidays').create(cr, uid, {'name': 'Allocation of 5 PLs', 'holiday_status_id': search_privilege_leave[0], 'employee_id': emp_record_id, 'number_of_days_temp': 5, 'type': 'add'}, context=context)
               
               
               self.pool.get('hr.holidays').holidays_first_validate(cr, uid, [create_id], context=context)
               self.pool.get('hr.holidays').holidays_validate(cr, uid, [create_id], context=context)
               
            ## Allocation of remaining 17 Privilege Leaves (PLs) at the end of 8 months from DOJ

            elif today_date == str(date_after_8months):
               
               create_id_after_8months = self.pool.get('hr.holidays').create(cr, uid, {'name': 'Allocation of 17 PLs', 'holiday_status_id': search_privilege_leave[0], 'employee_id': emp_record_id, 'number_of_days_temp': 17, 'type': 'add'}, context=context)
               
               
               self.pool.get('hr.holidays').holidays_first_validate(cr, uid, [create_id_after_8months], context=context)
               self.pool.get('hr.holidays').holidays_validate(cr, uid, [create_id_after_8months], context=context)

            ## On 1st January 2014, elapsing of the remaining unconsumed PLs in the PLs account of employee 
            ## On 1st January 2014, for all those employees who have completed more than 8 months, allocation of 22 PLs to the PLs account
            #elif (today_date > str(date_after_8months) and (no_of_years>=1 and no_of_years<=2) and remaining_leaves) :          
               
             #  search_emp_record = self.pool.get('hr.employee').search(cr,uid,[('id','=',record.employee_id.id)], context=context)
               
               #write_record = self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'remaining_leaves': 0.00})          

        
        return True

    def carry_forward_leaves(self, cr, uid, ids=None, context=None):
        from dateutil.relativedelta import relativedelta

        import datetime
        from datetime import datetime
        from datetime import timedelta
        from time import strftime
        from datetime import date

        from time import strftime
        today_date = strftime("%Y-%m-%d") 
        
        emp_search = self.pool.get('hr.employee').search(cr, uid, [('id', '>', 0)], context=context)

        
        print emp_search, "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"

        for record in self.pool.get('hr.employee').browse(cr, uid, emp_search):

            

            joining_date = record.join_date
            

            

            remaining_leaves = record.remaining_leaves
            

            joining_date_year = int(joining_date[:4])
            joining_date_month = int(joining_date[5:7])
            joining_date_date = int(joining_date[8:10]) 

            if joining_date:
                date_dt= datetime.strptime(joining_date, "%Y-%m-%d").date()
                today = datetime.today().date()
                tenure = relativedelta(today, date_dt)

            no_of_years = tenure.years
            

            date_after_8months = date(joining_date_year,joining_date_month,joining_date_date) + relativedelta(months=+8)
            

            search_privilege_leave = self.pool.get('hr.holidays.status').search(cr,uid,[('name','=','Privilege Leave (PL)')], context=context)

            search_sick_leave = self.pool.get('hr.holidays.status').search(cr,uid,[('name','=','Sick Leave (SL)')], context=context)

            search_emp_record = self.pool.get('hr.employee').search(cr,uid,[('id','>',0)], context=context)

            for h in self.pool.get('hr.employee').browse(cr,uid,search_emp_record):
                sick_leaves = h.sick_leaves            
            
                if sick_leaves > 15:
                    sick_leave_carry_forward_write_id = self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'sick_leaves': 0})
                

            # On 1st January, for all those employees who have completed 1 to 2 years of service tenure and the remaining leaves <=14, their remaining leaves will get carryforwarded to the next year 

            if ((no_of_years>=1 and no_of_years<=2) and remaining_leaves<=14):          
                create_id_after_8months_for_14PLs = self.pool.get('hr.holidays').create(cr, uid, {'name': 'Allocation of 22 PLs', 'holiday_status_id': search_privilege_leave[0], 'employee_id': record.id, 'number_of_days_temp': 22, 'type': 'add'}, context=context)
               
                self.pool.get('hr.holidays').holidays_first_validate(cr, uid, [create_id_after_8months_for_14PLs], context=context)
                self.pool.get('hr.holidays').holidays_validate(cr, uid, [create_id_after_8months_for_14PLs], context=context)

            elif ((no_of_years>=1 and no_of_years<=2) and remaining_leaves>14):
                remaining_leaves = record.remaining_leaves
                
                #create_id_for_more_than_14PLs = self.pool.get('hr.holidays').create(cr, uid, {'name': 'Allocation of 36 PLs', 'holiday_status_id': search_privilege_leave[0], 'employee_id': record.employee_id.id, 'number_of_days_temp': 36, 'type': 'add'}, context=context)
               
                #self.pool.get('hr.holidays').holidays_first_validate(cr, uid, [create_id_for_more_than_14PLs], context=context)
                #self.pool.get('hr.holidays').holidays_validate(cr, uid, [create_id_for_more_than_14PLs], context=context)

           # On 1st January, for all those employees who have completed 3 to 4 years of service tenure and the remaining leaves <=21, their remaining leaves will get carryforwarded to the next year 

            if ((no_of_years>=3 and no_of_years<=4) and remaining_leaves<=21):
                
                create_id_for_21PLs = self.pool.get('hr.holidays').create(cr, uid, {'name': 'Allocation of 22 PLs', 'holiday_status_id': search_privilege_leave[0], 'employee_id': record.id, 'number_of_days_temp': 22, 'type': 'add'}, context=context)
               
                self.pool.get('hr.holidays').holidays_first_validate(cr, uid, [create_id_for_21PLs], context=context)
                self.pool.get('hr.holidays').holidays_validate(cr, uid, [create_id_for_21PLs], context=context)

            elif ((no_of_years>=3 and no_of_years<=4) and remaining_leaves>21):
                remaining_leaves = record.remaining_leaves
                

           # On 1st January, for all those employees who have completed 5 to 6 years of service tenure and the remaining leaves <=21, their remaining leaves will get carryforwarded to the next year 

            if ((no_of_years>=5 and no_of_years<=6) and remaining_leaves<=28):
                
                create_id_for_28PLs = self.pool.get('hr.holidays').create(cr, uid, {'name': 'Allocation of 22 PLs', 'holiday_status_id': search_privilege_leave[0], 'employee_id': record.id, 'number_of_days_temp': 22, 'type': 'add'}, context=context)
               
                self.pool.get('hr.holidays').holidays_first_validate(cr, uid, [create_id_for_28PLs], context=context)
                self.pool.get('hr.holidays').holidays_validate(cr, uid, [create_id_for_28PLs], context=context)

            elif ((no_of_years>=5 and no_of_years<=6) and remaining_leaves>28):
                remaining_leaves = record.remaining_leaves
                

           # On 1st January, for all those employees who have completed more than 7 years of service tenure and the remaining leaves <=21, their remaining leaves will get carryforwarded to the next year 

            if (no_of_years>=7 and remaining_leaves<=42):
                
                create_id_for_42PLs = self.pool.get('hr.holidays').create(cr, uid, {'name': 'Allocation of 22 PLs', 'holiday_status_id': search_privilege_leave[0], 'employee_id': record.id, 'number_of_days_temp': 22, 'type': 'add'}, context=context)
               
                self.pool.get('hr.holidays').holidays_first_validate(cr, uid, [create_id_for_42PLs], context=context)
                self.pool.get('hr.holidays').holidays_validate(cr, uid, [create_id_for_42PLs], context=context)

            elif (no_of_years>=7 and remaining_leaves>42):
                remaining_leaves = record.remaining_leaves
                
        
        return True
        
    def holidays_confirm(self, cr, uid, ids, context=None):
        self.check_holidays(cr, uid, ids, context=context)
        #for record in self.browse(cr, uid, ids, context=context):
        #    if record.employee_id and record.employee_id.parent_id and record.employee_id.parent_id.user_id:
        #        self.message_subscribe_users(cr, uid, [record.id], user_ids=[record.employee_id.parent_id.user_id.id,record.employee_id.hro.id,51], context=context)
        return True
    
    
    def _get_number_of_days(self, date_from, date_to):
        """Returns a float equals to the timedelta between two dates given as string."""

        from datetime import datetime,date
        import datetime

        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
        to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
        timedelta = to_dt - from_dt
        diff_day = timedelta.days + float(timedelta.seconds) / 86400

        from datetime import datetime,date
        import datetime

        date_from_year = int(date_from[:4])
        date_from_month = int(date_from[5:7])
        date_from_date = int(date_from[8:10])

        date_to_year = int(date_to[:4])
        date_to_month = int(date_to[5:7])
        date_to_date = int(date_to[8:10])
        
        

        weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

        from datetime import date, timedelta as td

        d1 = date(date_from_year,date_from_month,date_from_date)
        d2 = date(date_to_year,date_to_month,date_to_date)

        print d1,d2, "----------------------------------------------------------------------"

        delta = d2 - d1

        count = 0.0
        for i in range(delta.days + 1):
            date_in_list =  d1 + td(days=i)
            
            
            week_number_list = datetime.datetime(date_in_list.year, date_in_list.month, date_in_list.day).weekday()
            
            
            if (weekdays[week_number_list] == 'Saturday' or weekdays[week_number_list] == 'Sunday'):   
                    count = count+1.0
            
        
        final_difference_days =  diff_day - count    


        return final_difference_days
        
    def _get_number_of_days_trip(self, date_from, date_to, business_trip):   # Function for Business Trips
        """Returns a float equals to the timedelta between two dates given as string."""

        from datetime import datetime,date
        import datetime

        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
        to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
        timedelta = to_dt - from_dt
        diff_day = timedelta.days + float(timedelta.seconds) / 86400

        from datetime import datetime,date
        import datetime

        date_from_year = int(date_from[:4])
        date_from_month = int(date_from[5:7])
        date_from_date = int(date_from[8:10])

        date_to_year = int(date_to[:4])
        date_to_month = int(date_to[5:7])
        date_to_date = int(date_to[8:10])
        
        

        weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

        from datetime import date, timedelta as td

        d1 = date(date_from_year,date_from_month,date_from_date)
        d2 = date(date_to_year,date_to_month,date_to_date)

        print d1,d2, business_trip, "----------------------------------------------------------------------"

        delta = d2 - d1

        count = 0.0
        for i in range(delta.days + 1):
            date_in_list =  d1 + td(days=i)
            
            
            week_number_list = datetime.datetime(date_in_list.year, date_in_list.month, date_in_list.day).weekday()
            
            
            if (weekdays[week_number_list] == 'Saturday' or weekdays[week_number_list] == 'Sunday'):   
                    count = count+1.0
            
        
        final_difference_days =  diff_day - count    


        return diff_day
        
    def onchange_date_from_trip(self, cr, uid, ids, date_to, date_from, business_trip):
        """
        If there are no date set for date_to, automatically set one 8 hours later than
        the date_from.
        Also update the number_of_days.
        """
        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

        result = {'value': {}}

        # No date_to set so far: automatically compute one 8 hours later
        if date_from and not date_to:
            date_to_with_delta = datetime.datetime.strptime(date_from, tools.DEFAULT_SERVER_DATETIME_FORMAT) + datetime.timedelta(hours=8)
            result['value']['date_to'] = str(date_to_with_delta)

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            diff_day = self._get_number_of_days_trip(date_from, date_to, business_trip)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1
        else:
            result['value']['number_of_days_temp'] = 0

        return result

    def onchange_date_to_trip(self, cr, uid, ids, date_to, date_from, business_trip):
        """
        Update the number_of_days.
        """

        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

        result = {'value': {}}

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            diff_day = self._get_number_of_days_trip(date_from, date_to, business_trip)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1
        else:
            result['value']['number_of_days_temp'] = 0

        return result


    def find_day_of_week(self, cr, uid, ids, context=None):
        
        for record in self.browse(cr, uid, ids, context=context):
            employee_id = record.employee_id.id
            date_from = record.date_from
            date_to = record.date_to

            

            date_from_year = int(date_from[:4])
            date_from_month = int(date_from[5:7])
            date_from_date = int(date_from[8:10])

            date_to_year = int(date_to[:4])
            date_to_month = int(date_to[5:7])
            date_to_date = int(date_to[8:10])

            
            from datetime import datetime,date
            import datetime
            week_number = datetime.datetime(date_from_year, date_from_month, date_from_date).weekday()

            weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

            if (weekdays[week_number] == 'Saturday' or weekdays[week_number] == 'Sunday'):
                print "ttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt"

            

            

            DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
            to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
            timedelta = to_dt - from_dt
            diff_day = timedelta.days + float(timedelta.seconds) / 86400
            diff_day_int = int(diff_day)
            difference_days = diff_day + 1.0
            difference_days_int = int(difference_days)
        
            

            from datetime import date, timedelta as td

            d1 = date(date_from_year,date_from_month,date_from_date)
            d2 = date(date_to_year,date_to_month,date_to_date)

            delta = d2 - d1     

            count = 0
            for i in range(delta.days + 1):
                date_in_list =  d1 + td(days=i)
                
                
                week_number_list = datetime.datetime(date_in_list.year, date_in_list.month, date_in_list.day).weekday()
                
                
                if (weekdays[week_number_list] == 'Saturday' or weekdays[week_number_list] == 'Sunday'):   
                    count = count+1
            
            final_difference_days =  difference_days_int - count
            
            
            


    def action_leave_request_confirm(self,cr,uid,ids,context=None):
        
        for record in self.browse(cr, uid, ids, context=context):

            if record.date_from==False:
               record.date_from = '2014-01-01 00:00:00'

            if record.date_to==False:
               record.date_to = '2014-01-01 00:00:00'


            employee_id = record.employee_id.id
            employee_status_of_confirmation = record.employee_id.status_of_confirmation
            joining_date = record.employee_id.join_date
            
            leave_record_type = record.type
            marital_status = record.employee_id.marital
            allow_leave_record_in_probationary_period = record.allow_leave_record_in_probationary_period
            no_of_confinements_post_joining = record.employee_id.no_of_confinements_post_joining
            

            date_from = record.date_from[:10]
            date_to = record.date_to[:10]
            
            print date_from, date_to, "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
            
            #from datetime import datetime,date
            #import datetime
            #from time import strftime
            #DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            
            #from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
            
            #print from_dt, "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
            #from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
            
            #from_date = from_dt.strftime("%Y-%m-%d")
            
            #print from_date, type(from_date),"iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
            
            

            compensatory_expiry_date = record.compensatory_expiry_date
            from time import strftime
            current_date = strftime("%Y-%m-%d")
            
            todays_date = strftime("%Y-%m-%d")
            
            date_to_year = int(date_to[:4])
            date_to_month = int(date_to[5:7])
            date_to_date = int(date_to[8:10])   
            
            date_from_year = int(date_from[:4])
            date_from_month = int(date_from[5:7])
            date_from_date = int(date_from[8:10])   
        
            current_year = int(current_date[:4])
            current_month = int(current_date[5:7])
            current_date = int(current_date[8:10])   

            joining_date_year = int(joining_date[:4])
            joining_date_month = int(joining_date[5:7])
            joining_date_date = int(joining_date[8:10])

            number_of_days = record.number_of_days_temp

            from dateutil.relativedelta import relativedelta

            import datetime
            from datetime import datetime
            from datetime import timedelta
            from time import strftime
            from datetime import date

            #Getting the date after 3 and 6 months from the date of joining

            date_after_3months = date(joining_date_year,joining_date_month,joining_date_date) + relativedelta(months=+3)
            date_after_6months = date(joining_date_year,joining_date_month,joining_date_date) + relativedelta(months=+6)
            date_after_6months_from_current_date = date(current_year,current_month,current_date) + relativedelta(months=+6)
            date_before_1day_from_current_date = date(current_year,current_month,current_date) + relativedelta(days=-1)
            
            date_before_1day_from_date_from = date(date_from_year,date_from_month,date_from_date) + relativedelta(days=-1)
            date_after_1day_from_date_to = date(date_to_year,date_to_month,date_to_date) + relativedelta(days=+1)
            
            print date_before_1day_from_current_date, "jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj"
            print date_before_1day_from_date_from, "mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm"
            print date_after_1day_from_date_to, "ttttttttttttttttttttttttt DATE AFTER 1 DAY FROM DATE TO ttttttttttttttttttttttttttttttt"
            
            
            #An Employee cannot apply for a leave in his probationary period

            if (date_from>=str(joining_date) and date_from<=str(date_after_3months) and leave_record_type == 'remove' and allow_leave_record_in_probationary_period == False and record.holiday_status_id.name!='Leave Without Pay (LWP)' and record.employee_id.name not in ('Arun Goenka','Bhakti Chandane')):
                raise osv.except_osv(_('Warning!'),_('You are not eligible to avail a leave in your probationary period'))
                
            if (date_from<=str(joining_date) and leave_record_type == 'remove'):
                raise osv.except_osv(_('Warning!'),_('You cannot apply for a leave before your joining date'))    

            #An Employee cannot apply for a leave beyond 6 months from current date
            
            if (employee_status_of_confirmation!='Confirmed' and record.employee_id.name not in ('Ujwala Pawade','Arun Goenka','Bhakti Chandane') and record.holiday_status_id.name!='Leave Without Pay (LWP)'):
                raise osv.except_osv(_('Warning!'),_('Since your status of Confirmation is pending, you cannot apply for a leave'))

            if date_from > str(date_after_6months_from_current_date):
                raise osv.except_osv(_('Warning!'),_('You cannot apply for a leave beyond 6 months from current date'))

            emp_gender = record.employee_id.gender
            emp_marital_status = record.employee_id.marital
            leave_type = record.holiday_status_id.name
            remaining_casual_leaves = record.remaining_casual_leaves
            remaining_privilege_leaves = record.remaining_privilege_leaves
            remaining_sick_leaves = record.remaining_sick_leaves
            remaining_compensatory_leaves = record.remaining_compensatory_leaves
            
            # An employee cannot combine Casual Leave with any other type of leave
            
            if (leave_type == 'Casual Leave (CL)' and leave_record_type == 'remove'):
                print "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww"
                
                #search_sick_leave = self.pool.get('hr.holidays.status').search(cr,uid,[('name','=','Sick Leave (SL)')], context=context)
                
                date_before_1day_from_date_from_str = str(date_before_1day_from_date_from)
                date_after_1day_from_date_to_str = str(date_after_1day_from_date_to)
                
                
                print ids[0], "hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh"
                search_all_leave_records = self.pool.get('hr.holidays').search(cr,uid,[('id','>',0),('type','=','remove')], context=context)
                #print search_all_leave_records, "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"
                for x in self.browse(cr, uid, search_all_leave_records):
                    from datetime import datetime,date
                    import datetime
                    from time import strftime
                    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
                    date_to_new = x.date_to   
                    date_from_new = x.date_from
                    print date_to_new, date_from_new  
                    to_dt = datetime.datetime.strptime(date_to_new, DATETIME_FORMAT)
                    from_dt = datetime.datetime.strptime(date_from_new, DATETIME_FORMAT)
                    print to_dt, "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&", x.id
                    print from_dt, "||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||", x.id
            
                    to_date = to_dt.strftime("%Y-%m-%d")
                    from_date = from_dt.strftime("%Y-%m-%d")
            
                    print to_date, type(to_date),"iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
                    print from_date, type(from_date),"iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
                    
                    date_to_sl = to_date
                    print date_to_sl, "llllllllllllllllllllllllllllllllllllllllll"
                    
                    date_from_sl = from_date
                    print date_from_sl, "-------------------------------------------"
                    
                    employee = x.employee_id.id
                    holiday_status = x.holiday_status_id.name
                    type_of_holiday = x.type
                    leave_state = x.state
                    
                    print employee_id, employee, "tttttttttttttttttttttttttttttttttttttttttttttt"
                    
                    print date_to_sl, date_before_1day_from_date_from_str, "666666666666666666666666666666666666666666666666666666666666666"
                    print date_from_sl, date_after_1day_from_date_to_str, "777777777777777777777777777777777777777777777777777777777777"
                    
                    if (employee_id == employee and holiday_status == 'Sick Leave (SL)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Sick Leave with Casual Leave'))
                        
                    elif (employee_id == employee and holiday_status == 'Compensatory-Off (CO)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Compensatory-Off with Casual Leave'))
                        
                    elif (employee_id == employee and holiday_status == 'Maternity Leave (ML)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Maternity Leave with Casual Leave'))
                        
                    elif (employee_id == employee and holiday_status == 'Paternity Leave (PAL)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Paternity Leave with Casual Leave'))
                        
                    elif (employee_id == employee and holiday_status == 'Wedding Leave (WL)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Wedding Leave with Casual Leave'))
                        
                    elif (employee_id == employee and holiday_status == 'Bereavement Leave (BL)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Bereavement Leave (BL) with Casual Leave'))
                        
                    elif (employee_id == employee and holiday_status == 'Restricted Holidays (RH)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Restricted Holiday with Casual Leave'))    
                        
                    elif (employee_id == employee and holiday_status == 'Privilege Leave (PL)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Privilege Leave with Casual Leave'))  
                        
                    elif (employee_id == employee and holiday_status == 'Leave Without Pay (LWP)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Leave Without Pay with Casual Leave'))     
                        
            # An employee cannot combine Compensatory-Off with any other type of leave
            
            if (leave_type == 'Compensatory-Off (CO)' and leave_record_type == 'remove'):
                print "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww ENTERED COMPENSATORY-OFF wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww"
                
                
                
                date_before_1day_from_date_from_str = str(date_before_1day_from_date_from)
                date_after_1day_from_date_to_str = str(date_after_1day_from_date_to)
                
                
                search_all_leave_records = self.pool.get('hr.holidays').search(cr,uid,[('id','>',0),('type','=','remove')], context=context)
                
                print search_all_leave_records, "----------------LIST OF ALL LEAVE RECORDS-------------------------"
                
                for x in self.browse(cr, uid, search_all_leave_records):
                    
                    from datetime import datetime,date
                    import datetime
                    from time import strftime
                    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            
                    to_dt = datetime.datetime.strptime(x.date_to, DATETIME_FORMAT)
                    from_dt = datetime.datetime.strptime(x.date_from, DATETIME_FORMAT)
            
                    print to_dt, "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                    print from_dt, "ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo"
            
                    to_date = to_dt.strftime("%Y-%m-%d")
                    from_date = from_dt.strftime("%Y-%m-%d")
            
                    print to_date, type(to_date),"iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
                    print from_date, type(from_date),"iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
                    
                    date_to_sl = to_date
                    print date_to_sl, "llllllllllllllllllllllllllllllllllllllllll"
                    
                    date_from_sl = from_date
                    print date_from_sl, "llllllllllllllllllllllllllllllllllllllllll"
                    
                    employee = x.employee_id.id
                    holiday_status = x.holiday_status_id.name
                    type_of_holiday = x.type
                    leave_state = x.state
                    
                    print employee_id, employee, "tttttttttttttttttttttttttttttttttttttttttttttt"
                    
                    print date_to_sl, date_before_1day_from_date_from_str, "*****************************************************"
                    print date_from_sl, date_after_1day_from_date_to_str, "*****************************************************"
                    
                    
                    if (employee_id == employee and holiday_status == 'Sick Leave (SL)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Sick Leave with Compensatory-Off'))
                        
                    elif (employee_id == employee and holiday_status == 'Casual Leave (CL)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Casual Leave with Compensatory-Off'))
                        
                    elif (employee_id == employee and holiday_status == 'Maternity Leave (ML)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Maternity Leave with Compensatory-Off'))
                        
                    elif (employee_id == employee and holiday_status == 'Paternity Leave (PAL)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrr PATERNITY LEAVE FOUND rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Paternity Leave with Compensatory-Off'))
                        
                    elif (employee_id == employee and holiday_status == 'Wedding Leave (WL)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "ddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Wedding Leave with Compensatory-Off'))
                        
                    elif (employee_id == employee and holiday_status == 'Bereavement Leave (BL)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Bereavement Leave (BL) with Compensatory-Off'))
                        
                    elif (employee_id == employee and holiday_status == 'Restricted Holidays (RH)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Restricted Holiday with Compensatory-Off'))  
                        
                    elif (employee_id == employee and holiday_status == 'Privilege Leave (PL)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Privilege Leave with Compensatory-Off'))   
                        
                    elif (employee_id == employee and holiday_status == 'Leave Without Pay (LWP)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Leave Without Pay with Compensatory-Off'))     
            
            # An employee cannot combine Restricted Holiday with any other type of leave
            
            if (leave_type == 'Restricted Holidays (RH)' and leave_record_type == 'remove'):
                print "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww"
                
                
                
                date_before_1day_from_date_from_str = str(date_before_1day_from_date_from)
                date_after_1day_from_date_to_str = str(date_after_1day_from_date_to)
                
                
                
                search_all_leave_records = self.pool.get('hr.holidays').search(cr,uid,[('id','>',0),('type','=','remove')], context=context)
                
                for x in self.browse(cr, uid, search_all_leave_records):
                    
                    from datetime import datetime,date
                    import datetime
                    from time import strftime
                    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            
                    to_dt = datetime.datetime.strptime(x.date_to, DATETIME_FORMAT)
                    from_dt = datetime.datetime.strptime(x.date_from, DATETIME_FORMAT)
            
                    print to_dt, "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                    print from_dt, "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                    
            
                    to_date = to_dt.strftime("%Y-%m-%d")
                    from_date = from_dt.strftime("%Y-%m-%d")
            
                    print to_date, type(to_date),"iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
                    print from_date, type(from_date),"iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
                    
                    date_to_sl = to_date
                    print date_to_sl, "llllllllllllllllllllllllllllllllllllllllll"
                    
                    date_from_sl = from_date
                    print date_from_sl, "llllllllllllllllllllllllllllllllllllllllll"
                    
                    employee = x.employee_id.id
                    holiday_status = x.holiday_status_id.name
                    type_of_holiday = x.type
                    leave_state = x.state
                    
                    print employee_id, employee, "tttttttttttttttttttttttttttttttttttttttttttttt"
                    
                    print date_to_sl, date_before_1day_from_date_from_str, "*****************************************************"
                    print date_from_sl, date_after_1day_from_date_to_str, "*****************************************************"
                    
                    
                    if (employee_id == employee and holiday_status == 'Sick Leave (SL)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Sick Leave with Restricted Holiday'))
                        
                    elif (employee_id == employee and holiday_status == 'Casual Leave (CL)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Casual Leave with Restricted Holiday'))
                        
                    elif (employee_id == employee and holiday_status == 'Maternity Leave (ML)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Maternity Leave with Restricted Holiday'))
                        
                    elif (employee_id == employee and holiday_status == 'Paternity Leave (PAL)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Paternity Leave with Restricted Holiday'))
                        
                    elif (employee_id == employee and holiday_status == 'Wedding Leave (WL)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Wedding Leave with Restricted Holiday'))
                        
                    elif (employee_id == employee and holiday_status == 'Bereavement Leave (BL)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Bereavement Leave (BL) with Restricted Holiday'))
                        
                    elif (employee_id == employee and holiday_status == 'Compensatory-Off (CO)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Compensatory-Off with Restricted Holiday'))    
                        
                    elif (employee_id == employee and holiday_status == 'Privilege Leave (PL)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Privilege Leave with Restricted Holiday'))   
                        
                    elif (employee_id == employee and holiday_status == 'Leave Without Pay (LWP)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Leave Without Pay with Restricted Holiday'))      
            
            # An employee cannot combine Sick Leave with Casual Leave, Compensatory-Off, Restricted Holiday
            
            if (leave_type == 'Sick Leave (SL)' and leave_record_type == 'remove'):
                print "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww"
                
                #search_sick_leave = self.pool.get('hr.holidays.status').search(cr,uid,[('name','=','Casual Leave (CL)')], context=context)
                
                date_before_1day_from_date_from_str = str(date_before_1day_from_date_from)
                date_after_1day_from_date_to_str = str(date_after_1day_from_date_to)
                
                print 
                search_all_leave_records = self.pool.get('hr.holidays').search(cr,uid,[('id','>',0),('type','=','remove')], context=context)
                
                for x in self.browse(cr, uid, search_all_leave_records):
                    
                    from datetime import datetime,date
                    import datetime
                    from time import strftime
                    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            
                    to_dt = datetime.datetime.strptime(x.date_to, DATETIME_FORMAT)
                    from_dt = datetime.datetime.strptime(x.date_from, DATETIME_FORMAT)
            
                    print to_dt, "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                    print from_dt, "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
            
                    to_date = to_dt.strftime("%Y-%m-%d")
                    from_date = from_dt.strftime("%Y-%m-%d")
            
                    print to_date, type(to_date),"iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
                    print from_date, type(from_date),"iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
                    
                    date_to_sl = to_date
                    print date_to_sl, "llllllllllllllllllllllllllllllllllllllllll"
                    
                    date_from_sl = from_date
                    print date_from_sl, "llllllllllllllllllllllllllllllllllllllllll"
                    
                    employee = x.employee_id.id
                    holiday_status = x.holiday_status_id.name
                    type_of_holiday = x.type
                    leave_state = x.state
                    
                    print employee_id, employee, "tttttttttttttttttttttttttttttttttttttttttttttt"
                    
                    print date_to_sl, date_before_1day_from_date_from_str, "*****************************************************"
                    print date_from_sl, date_after_1day_from_date_to_str, "*****************************************************"
                    
                    if (employee_id == employee and holiday_status == 'Casual Leave (CL)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Casual Leave with Sick Leave'))
                        
                    if (employee_id == employee and holiday_status == 'Compensatory-Off (CO)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Compensatory-Off with Sick Leave'))
                        
                    if (employee_id == employee and holiday_status == 'Restricted Holidays (RH)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Restricted Holidays with Sick Leave'))    
                        
            
            # An employee cannot combine Wedding Leave with Casual Leave, Compensatory-Off, Restricted Holiday
            
            if (leave_type == 'Wedding Leave (WL)' and leave_record_type == 'remove'):
                print "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww"
                
                #search_sick_leave = self.pool.get('hr.holidays.status').search(cr,uid,[('name','=','Casual Leave (CL)')], context=context)
                
                date_before_1day_from_date_from_str = str(date_before_1day_from_date_from)
                date_after_1day_from_date_to_str = str(date_after_1day_from_date_to)
                
                
                
                search_all_leave_records = self.pool.get('hr.holidays').search(cr,uid,[('id','>',0),('type','=','remove')], context=context)
                
                for x in self.browse(cr, uid, search_all_leave_records):
                    
                    from datetime import datetime,date
                    import datetime
                    from time import strftime
                    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            
                    to_dt = datetime.datetime.strptime(x.date_to, DATETIME_FORMAT)
                    from_dt = datetime.datetime.strptime(x.date_from, DATETIME_FORMAT)
            
                    print to_dt, "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                    print from_dt, "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
            
                    to_date = to_dt.strftime("%Y-%m-%d")
                    from_date = from_dt.strftime("%Y-%m-%d")
            
                    print to_date, type(to_date),"iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
                    print from_date, type(from_date),"iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
                    
                    date_to_sl = to_date
                    print date_to_sl, "llllllllllllllllllllllllllllllllllllllllll"
                    
                    date_from_sl = from_date
                    print date_from_sl, "llllllllllllllllllllllllllllllllllllllllll"
                    
                    employee = x.employee_id.id
                    holiday_status = x.holiday_status_id.name
                    type_of_holiday = x.type
                    leave_state = x.state
                    
                    print employee_id, employee, "tttttttttttttttttttttttttttttttttttttttttttttt"
                    
                    print date_to_sl, date_before_1day_from_date_from_str, "*****************************************************"
                    print date_from_sl, date_after_1day_from_date_to_str, "*****************************************************"
                    
                    if (employee_id == employee and holiday_status == 'Casual Leave (CL)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Casual Leave with Wedding Leave'))
                        
                    if (employee_id == employee and holiday_status == 'Compensatory-Off (CO)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Compensatory-Off with Wedding Leave'))
                        
                    if (employee_id == employee and holiday_status == 'Restricted Holidays (RH)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Restricted Holidays with Wedding Leave'))       
                        
            # An employee cannot combine Maternity Leave with Casual Leave, Compensatory-Off, Restricted Holiday
            
            if (leave_type == 'Maternity Leave (ML)' and leave_record_type == 'remove'):
                print "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww"
                
                #search_sick_leave = self.pool.get('hr.holidays.status').search(cr,uid,[('name','=','Casual Leave (CL)')], context=context)
                
                date_before_1day_from_date_from_str = str(date_before_1day_from_date_from)
                date_after_1day_from_date_to_str = str(date_after_1day_from_date_to)
                
                
                search_all_leave_records = self.pool.get('hr.holidays').search(cr,uid,[('id','>',0),('type','=','remove')], context=context)
                
                for x in self.browse(cr, uid, search_all_leave_records):
                    
                    from datetime import datetime,date
                    import datetime
                    from time import strftime
                    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            
                    to_dt = datetime.datetime.strptime(x.date_to, DATETIME_FORMAT)
                    from_dt = datetime.datetime.strptime(x.date_from, DATETIME_FORMAT)
            
                    print to_dt, "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                    print from_dt, "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
            
                    to_date = to_dt.strftime("%Y-%m-%d")
                    from_date = from_dt.strftime("%Y-%m-%d")
            
                    print to_date, type(to_date),"iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
                    print from_date, type(from_date),"iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
                    
                    date_to_sl = to_date
                    print date_to_sl, "llllllllllllllllllllllllllllllllllllllllll"
                    
                    date_from_sl = from_date
                    print date_from_sl, "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
                    
                    employee = x.employee_id.id
                    holiday_status = x.holiday_status_id.name
                    type_of_holiday = x.type
                    leave_state = x.state
                    
                    print employee_id, employee, "tttttttttttttttttttttttttttttttttttttttttttttt"
                    
                    print date_to_sl, date_before_1day_from_date_from_str, "*****************************************************"
                    print date_from_sl, date_after_1day_from_date_to_str, "*****************************************************"
                    
                    
                    if (employee_id == employee and holiday_status == 'Casual Leave (CL)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Casual Leave with Maternity Leave'))
                        
                    if (employee_id == employee and holiday_status == 'Compensatory-Off (CO)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Compensatory-Off with Maternity Leave'))
                        
                    if (employee_id == employee and holiday_status == 'Restricted Holidays (RH)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Restricted Holidays with Maternity Leave'))                   
                        
            # An employee cannot combine Paternity Leave with Casual Leave, Compensatory-Off, Restricted Holiday
            
            if (leave_type == 'Paternity Leave (PAL)' and leave_record_type == 'remove'):
                print "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww"
                
                #search_sick_leave = self.pool.get('hr.holidays.status').search(cr,uid,[('name','=','Casual Leave (CL)')], context=context)
                
                date_before_1day_from_date_from_str = str(date_before_1day_from_date_from)
                date_after_1day_from_date_to_str = str(date_after_1day_from_date_to)
                
                
                search_all_leave_records = self.pool.get('hr.holidays').search(cr,uid,[('id','>',0),('type','=','remove')], context=context)
                
                for x in self.browse(cr, uid, search_all_leave_records):
                    
                    from datetime import datetime,date
                    import datetime
                    from time import strftime
                    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            
                    to_dt = datetime.datetime.strptime(x.date_to, DATETIME_FORMAT)
                    from_dt = datetime.datetime.strptime(x.date_from, DATETIME_FORMAT)
            
                    print to_dt, "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                    print from_dt, "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
            
                    to_date = to_dt.strftime("%Y-%m-%d")
                    from_date = from_dt.strftime("%Y-%m-%d")
            
                    print to_date, type(to_date),"iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
                    print from_date, type(from_date),"iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
                    
                    date_to_sl = to_date
                    print date_to_sl, "llllllllllllllllllllllllllllllllllllllllll"
                    
                    date_from_sl = from_date
                    print date_from_sl, "llllllllllllllllllllllllllllllllllllllllll"
                    
                    employee = x.employee_id.id
                    holiday_status = x.holiday_status_id.name
                    type_of_holiday = x.type
                    leave_state = x.state
                    
                    print employee_id, employee, "tttttttttttttttttttttttttttttttttttttttttttttt"
                    
                    print date_to_sl, date_before_1day_from_date_from_str, "*****************************************************"
                    print date_from_sl, date_after_1day_from_date_to_str, "*****************************************************"
                    
                    
                    if (employee_id == employee and holiday_status == 'Casual Leave (CL)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Casual Leave with Paternity Leave'))
                        
                    if (employee_id == employee and holiday_status == 'Compensatory-Off (CO)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Compensatory-Off with Paternity Leave'))
                        
                    if (employee_id == employee and holiday_status == 'Restricted Holidays (RH)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Restricted Holidays with Paternity Leave')) 
                        
            # An employee cannot combine Leave Without Pay with Casual Leave, Compensatory-Off, Restricted Holiday
            
            if (leave_type == 'Leave Without Pay (LWP)' and leave_record_type == 'remove'):
                print "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww"
                
                #search_sick_leave = self.pool.get('hr.holidays.status').search(cr,uid,[('name','=','Casual Leave (CL)')], context=context)
                
                date_before_1day_from_date_from_str = str(date_before_1day_from_date_from)
                date_after_1day_from_date_to_str = str(date_after_1day_from_date_to)
                
                
                
                search_all_leave_records = self.pool.get('hr.holidays').search(cr,uid,[('id','>',0),('type','=','remove')], context=context)
                
                for x in self.browse(cr, uid, search_all_leave_records):
                    
                    from datetime import datetime,date
                    import datetime
                    from time import strftime
                    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            
                    to_dt = datetime.datetime.strptime(x.date_to, DATETIME_FORMAT)
                    from_dt = datetime.datetime.strptime(x.date_from, DATETIME_FORMAT)
            
                    print to_dt, "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                    print from_dt, "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                    
            
                    to_date = to_dt.strftime("%Y-%m-%d")
                    from_date = from_dt.strftime("%Y-%m-%d")
            
                    print to_date, type(to_date),"iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
                    print from_date, type(from_date),"iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
                    
                    date_to_sl = to_date
                    print date_to_sl, "llllllllllllllllllllllllllllllllllllllllll"
                    
                    date_from_sl = from_date
                    print date_from_sl, "llllllllllllllllllllllllllllllllllllllllll"
                    
                    employee = x.employee_id.id
                    holiday_status = x.holiday_status_id.name
                    type_of_holiday = x.type
                    leave_state = x.state
                    
                    print employee_id, employee, "tttttttttttttttttttttttttttttttttttttttttttttt"
                    
                    print date_to_sl, date_before_1day_from_date_from_str, "*****************************************************"
                    print date_from_sl, date_after_1day_from_date_to, "*****************************************************"
                    
                    
                    if (employee_id == employee and holiday_status == 'Casual Leave (CL)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Casual Leave with Leave Without Pay'))
                        
                    if (employee_id == employee and holiday_status == 'Compensatory-Off (CO)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Compensatory-Off with Leave Without Pay'))
                        
                    if (employee_id == employee and holiday_status == 'Restricted Holidays (RH)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Restricted Holidays with Leave Without Pay (LWP)'))                                                 
            
            # An employee cannot combine Bereavement Leave with Casual Leave, Compensatory-Off, Restricted Holiday
            
            if (leave_type == 'Bereavement Leave (BL)' and leave_record_type == 'remove'):
                print "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww"
                
                #search_sick_leave = self.pool.get('hr.holidays.status').search(cr,uid,[('name','=','Casual Leave (CL)')], context=context)
                
                date_before_1day_from_date_from_str = str(date_before_1day_from_date_from)
                date_after_1day_from_date_to_str = str(date_after_1day_from_date_to)
                
                
                search_all_leave_records = self.pool.get('hr.holidays').search(cr,uid,[('id','>',0),('type','=','remove')], context=context)
                
                for x in self.browse(cr, uid, search_all_leave_records):
                    
                    from datetime import datetime,date
                    import datetime
                    from time import strftime
                    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            
                    to_dt = datetime.datetime.strptime(x.date_to, DATETIME_FORMAT)
                    from_dt = datetime.datetime.strptime(x.date_from, DATETIME_FORMAT)
            
                    print to_dt, "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                    print from_dt, "tttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt"
            
                    to_date = to_dt.strftime("%Y-%m-%d")
                    from_date = from_dt.strftime("%Y-%m-%d")
            
                    print to_date, type(to_date),"iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
                    print from_date, type(from_date),"qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq"
                    
                    date_to_sl = to_date
                    print date_to_sl, "llllllllllllllllllllllllllllllllllllllllll"
                    
                    date_from_sl = from_date
                    print date_from_sl, "llllllllllllllllllllllllllllllllllllllllll"
                    
                    employee = x.employee_id.id
                    holiday_status = x.holiday_status_id.name
                    type_of_holiday = x.type
                    leave_state = x.state
                    
                    print employee_id, employee, "tttttttttttttttttttttttttttttttttttttttttttttt"
                    
                    print date_to_sl, date_before_1day_from_date_from_str, "*****************************************************"
                    print date_from_sl, date_after_1day_from_date_to_str, "*****************************************************"
                    
                    
                    if (employee_id == employee and holiday_status == 'Casual Leave (CL)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Casual Leave with Bereavement Leave'))
                        
                    if (employee_id == employee and holiday_status == 'Compensatory-Off (CO)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Compensatory-Off with Bereavement Leave'))
                        
                    if (employee_id == employee and holiday_status == 'Restricted Holidays (RH)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Restricted Holidays with Bereavement Leave'))                                                 
            
            # An employee cannot combine Privilege Leave with Casual Leave, Compensatory-Off, Restricted Holiday
            
            if (leave_type == 'Privilege Leave (PL)' and leave_record_type == 'remove'):
                print "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww"
                
                #search_sick_leave = self.pool.get('hr.holidays.status').search(cr,uid,[('name','=','Casual Leave (CL)')], context=context)
                
                date_before_1day_from_date_from_str = str(date_before_1day_from_date_from)
                date_after_1day_from_date_to_str = str(date_after_1day_from_date_to)
                
                
                
                search_all_leave_records = self.pool.get('hr.holidays').search(cr,uid,[('id','>',0),('type','=','remove')], context=context)
                
                for x in self.browse(cr, uid, search_all_leave_records):
                    
                    from datetime import datetime,date
                    import datetime
                    from time import strftime
                    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            
                    to_dt = datetime.datetime.strptime(x.date_to, DATETIME_FORMAT)
                    from_dt = datetime.datetime.strptime(x.date_from, DATETIME_FORMAT)
            
                    print to_dt, "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                    print from_dt, "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                    
            
                    to_date = to_dt.strftime("%Y-%m-%d")
                    from_date = from_dt.strftime("%Y-%m-%d")
            
                    print to_date, type(to_date),"iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
                    print from_date, type(from_date),"iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
                    
                    date_to_sl = to_date
                    print date_to_sl, "llllllllllllllllllllllllllllllllllllllllll"
                    
                    date_from_sl = from_date
                    print date_from_sl, "llllllllllllllllllllllllllllllllllllllllll"
                    
                    employee = x.employee_id.id
                    holiday_status = x.holiday_status_id.name
                    type_of_holiday = x.type
                    leave_state = x.state
                    
                    print employee_id, employee, "tttttttttttttttttttttttttttttttttttttttttttttt"
                    
                    print date_to_sl, date_before_1day_from_date_from_str, "*****************************************************"
                    print date_from_sl, date_after_1day_from_date_to_str, "*****************************************************"
                    
                    
                    if (employee_id == employee and holiday_status == 'Casual Leave (CL)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Casual Leave with Privilege Leave'))
                        
                    if (employee_id == employee and holiday_status == 'Compensatory-Off (CO)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Compensatory-Off with Privilege Leave'))
                        
                    if (employee_id == employee and holiday_status == 'Restricted Holidays (RH)' and type_of_holiday == 'remove' and (date_to_sl == date_before_1day_from_date_from_str or date_from_sl == date_after_1day_from_date_to_str) and leave_state == 'confirm'):
                        print "rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr"
                        raise osv.except_osv(_('Warning!'),_('You cannot combine Restricted Holidays with Privilege Leave'))                                                 
            
            #If an employee does not have any COs remaining in his COs account, he won't be able to apply for a CO
                
            if (leave_type == 'Compensatory-Off (CO)' and leave_record_type == 'remove' and remaining_compensatory_leaves == 0.00):
                raise osv.except_osv(_('Error!'),_("You do not have any compensatory off's remaining in your CO's account"))        
            
            #If an employee does not have any SLs remaining in his SLs account, he won't be able to apply for a SL
                
            if (leave_type == 'Sick Leave (SL)' and leave_record_type == 'remove' and remaining_sick_leaves == 0.00):
                raise osv.except_osv(_('Error!'),_("You do not have any sick leaves remaining in your SL's account"))        
                
            #If an employee does not have any PLs remaining in his PLs account, he won't be able to apply for a PL
                
            if (leave_type == 'Privilege Leave (PL)' and leave_record_type == 'remove' and remaining_privilege_leaves == 0.00):
                raise osv.except_osv(_('Error!'),_("You do not have any privilege leaves remaining in your PL's account"))        
            
            #If an employee does not have any CLs remaining in his CLs account, he won't be able to apply for a CL
                
            if (leave_type == 'Casual Leave (CL)' and leave_record_type == 'remove' and remaining_casual_leaves == 0.00):
                raise osv.except_osv(_('Error!'),_("You do not have any casual leaves remaining in your CL's account"))    
                
            #A male employee cannot apply for a Maternity Leave 

            if (emp_gender== 'male' and leave_type == 'Maternity Leave (ML)' and leave_record_type == 'remove'):
                raise osv.except_osv(_('Error!'),_('You are not eligible to avail a Maternity Leave'))

            #A male employee who is single cannot apply for a Paternity Leave 

            if (emp_gender== 'male' and marital_status == 'single' and leave_type == 'Paternity Leave (PAL)' and leave_record_type == 'remove'):
                raise osv.except_osv(_('Error!'),_('You are not eligible to avail a Paternity Leave'))

            #A female employee cannot apply for a Paternity Leave 

            if (emp_gender== 'female' and leave_type == 'Paternity Leave (PAL)' and leave_record_type == 'remove'):
                raise osv.except_osv(_('Error!'),_('You are not eligible to avail a Paternity Leave'))

            #A female employee who is single cannot apply for a Maternity Leave 

            if (emp_gender== 'female' and emp_marital_status== 'single' and leave_type == 'Maternity Leave (ML)' and leave_record_type == 'remove'):
                raise osv.except_osv(_('Error!'),_('You are not eligible to avail a Maternity Leave'))

            

            if (emp_gender== 'female' and emp_marital_status== 'married' and leave_type == 'Maternity Leave (ML)' and leave_record_type == 'remove' and no_of_confinements_post_joining > 2):
                raise osv.except_osv(_('Error!'),_('You are not eligible to avail a Maternity Leave'))
                
            print date_from, date_to, todays_date, "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"    
            if (leave_type == 'Sick Leave (SL)' and (date_from > todays_date or date_to > todays_date)):
                print "ppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp"
                raise osv.except_osv(_('Error!'),_('You cannot apply for a Sick Leave in advance'))

            
            today_date = strftime("%Y-%m-%d")
            
            import datetime
            DATETIME_FORMAT = "%Y-%m-%d"
            today_date = datetime.datetime.strptime(today_date, DATETIME_FORMAT)
            joining_date = datetime.datetime.strptime(joining_date, DATETIME_FORMAT)
            timedelta = today_date - joining_date
            diff_day = timedelta.days

            # An employee whose CO limit has been expired cannot apply for a CO            
            
            if compensatory_expiry_date:
                if date_from > compensatory_expiry_date:
                    raise osv.except_osv(_('Warning!'),_('You cannot avail a Compensatory-Off since your limit of availing the CO has already been expired'))    

            
            # An employee who has not completed 6 months of service tenure in the organization cannot apply for a Maternity Leave            

            if (leave_type == 'Maternity Leave (ML)' and date_from<str(date_after_6months) and leave_record_type == 'remove'):
              raise osv.except_osv(_('Warning!'),_('You cannot avail for a Maternity leave because your tenure is less than 6 months in the organization'))  

            # An employee who has not completed 6 months of service tenure in the organization cannot apply for a Wedding Leave            

            if (leave_type == 'Wedding Leave (WL)' and date_from<str(date_after_6months) and leave_record_type == 'remove'):
              raise osv.except_osv(_('Warning!'),_('You cannot avail for a Wedding leave because your tenure is less than 6 months in the organization'))
            
            # An employee who has not completed 6 months of service tenure in the organization cannot apply for a Paternity Leave            

            if (leave_type == 'Paternity Leave (PAL)' and date_from<str(date_after_6months) and leave_record_type == 'remove'):
              raise osv.except_osv(_('Warning!'),_('You cannot avail for a Paternity leave because your tenure is less than 6 months in the organization'))

            date_from_year = int(date_from[:4])
            date_from_month = int(date_from[5:7])
            date_from_date = int(date_from[8:10])

            date_after_3months_from_leave_application_date = date(date_from_year,date_from_month,date_from_date) + relativedelta(months=+3)
            

            # An employee can apply for Maternity Leave only for a period of 3 months  

            if (leave_type == 'Maternity Leave (ML)' and date_to>str(date_after_3months_from_leave_application_date) and leave_record_type == 'remove'):
                raise osv.except_osv(_('Warning!'),_('You can apply for a Maternity leave only for a period of 3 months')) 
            
            # An employee can apply for only 3 Casual Leaves together

            if (leave_type == 'Casual Leave (CL)' and number_of_days>3 and leave_record_type == 'remove'):
                raise osv.except_osv(_('Warning!'),_('Only 3 Casual Leaves can be applied together'))
            
            # An employee can apply for only 5 Wedding Leaves           

            if (leave_type == 'Wedding Leave (WL)' and number_of_days>5 and leave_record_type == 'remove'):
                raise osv.except_osv(_('Warning!'),_('You are eligible for only 5 Wedding Leaves'))

            

            # An employee can apply for only 5 Paternity Leaves                       

            if (leave_type == 'Paternity Leave (PAL)' and number_of_days>5 and leave_record_type == 'remove'):
                
                raise osv.except_osv(_('Warning!'),_('You can apply for only 5 Paternity Leaves'))

            # An employee can apply for only 2 Bereavement Leaves

            if (leave_type == 'Bereavement Leave (BL)' and number_of_days>2 and leave_record_type == 'remove'):
                
                raise osv.except_osv(_('Warning!'),_('You can apply for only 2 Bereavement Leaves'))
            
            from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
            timedelta_diff = from_dt - today_date 
            difference_days = timedelta_diff.days



            from time import strftime
            date_from = record.date_from[:10]
            date_to = record.date_to[:10]
            today_date = strftime("%Y-%m-%d")
            current_date = strftime("%Y-%m-%d")
            leave_type = record.holiday_status_id.name
            leave_record_type = record.type
            import datetime
            DATETIME_FORMAT = "%Y-%m-%d"
            today_date = datetime.datetime.strptime(today_date, DATETIME_FORMAT)
            from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
            timedelta_diff = from_dt - today_date 
            difference_days = timedelta_diff.days
            allow_leave_request = record.allow_leave_request

            wedding_card = record.wedding_card

            maternity_certificate = record.maternity_certificate

            no_of_days = record.number_of_days_temp

            # When an employee applies for Maternity Leave she has to upload an attachment as a proof of the Maternity Leave
            
            if (leave_type == 'Maternity Leave (ML)'):
                if not maternity_certificate:
                    

                    raise osv.except_osv(_('Warning!'),_('Please upload an attachment for availing Maternity Leave'))
            
            # When an employee applies for wedding leave, he/she has to attach a Wedding Card

            if (leave_type == 'Wedding Leave (WL)'):
                if not wedding_card:

                    raise osv.except_osv(_('Warning!'),_('Please attach the Wedding Card'))

            # When an employee applies for Sick leave, he has to attach a Medical Certificate

            if (leave_type == 'Sick Leave (SL)' and no_of_days>1):
                
                if not record.medical_certificate_line:

                    raise osv.except_osv(_('Warning!'),_('Please attach the medical certificate'))

                elif record.medical_certificate_line:
                    search_medical_certificate = self.pool.get('medical.certificate').search(cr,uid,[('medical_certificate_number','=',ids[0])], context=context)                
                    
                    for t in self.pool.get('medical.certificate').browse(cr, uid, search_medical_certificate):
                            medical_certificate_file = t.medical_certificate_file
                            if not medical_certificate_file:
                                raise osv.except_osv(_('Warning!'),_('Please attach the medical certificate'))


            is_optional_item_exists = False
            is_maternity_leave = False
            is_wedding_leave = False
            is_casual_leave = False
            is_compensatory_off = False
            is_paternity_leave = False

            current_year = int(current_date[:4])
            current_month = int(current_date[5:7])
            current_date = int(current_date[8:10])
            
            from datetime import date
            from dateutil.relativedelta import relativedelta
            
            current_date_date = date(current_year,current_month,current_date)
            date_after_3months_from_current_date = date(current_year,current_month,current_date) + relativedelta(months=+3)
            date_after_1month_from_current_date = date(current_year,current_month,current_date) + relativedelta(months=+1)
            date_before_1month_from_current_date = date(current_year,current_month,current_date) + relativedelta(months=-1)
            date_after_2months_from_current_date = date(current_year,current_month,current_date) + relativedelta(months=+2)
            date_after_6months_from_current_date = date(current_year,current_month,current_date) + relativedelta(months=+6)

            

            if (leave_type == 'Casual Leave (CL)' and difference_days>=0 and difference_days<7 and allow_leave_request==False):
               
               is_casual_leave = True
               
            #elif (leave_type == 'Casual Leave (CL)' and (date_from<str(date_before_1month_from_current_date) or date_to<str(date_before_1month_from_current_date)) and allow_leave_request==False):
               
             #  raise osv.except_osv(_('Warning!'),_("You can apply for a backdated Casual Leave only upto 1 month back from current date"))
               
            #elif (leave_type == 'Sick Leave (SL)' and (date_from<str(date_before_1month_from_current_date) or date_to<str(date_before_1month_from_current_date)) and allow_leave_request==False):
               
             #  raise osv.except_osv(_('Warning!'),_("You can apply for a backdated Sick Leave only upto 1 month back from current date"))
               
            elif (leave_type == 'Bereavement Leave (BL)' and (date_from<str(date_before_1month_from_current_date) or date_to<str(date_before_1month_from_current_date)) and allow_leave_request==False):
               
               raise osv.except_osv(_('Warning!'),_("You can apply for a backdated Bereavement Leave only upto 1 month back from current date"))
               
            elif (leave_type == 'Leave Without Pay (LWP)' and (date_from<str(date_before_1month_from_current_date) or date_to<str(date_before_1month_from_current_date)) and allow_leave_request==False):
               
               raise osv.except_osv(_('Warning!'),_("You can apply for a backdated Leave Without Pay (LWP) only upto 1 month back from current date"))


            elif (leave_type == 'Wedding Leave (WL)' and date_from<str(date_after_1month_from_current_date) and date_from>=str(current_date_date) and allow_leave_request==False):
                
                is_wedding_leave = True
                
            #elif (leave_type == 'Wedding Leave (WL)' and date_from<str(current_date_date) and allow_leave_request==False):
                
            #    raise osv.except_osv(_('Warning!'),_("You cannot apply for a backdated Wedding Leave"))
                

            elif (leave_type == 'Paternity Leave (PAL)' and date_from<str(date_after_2months_from_current_date) and date_from>=str(current_date_date) and allow_leave_request==False):
                
                is_paternity_leave = True
                
            #elif (leave_type == 'Paternity Leave (PAL)' and date_from<str(current_date_date) and allow_leave_request==False):
                
             #   raise osv.except_osv(_('Warning!'),_("You cannot apply for a backdated Paternity Leave"))
                

            elif (leave_type == 'Compensatory-Off (CO)' and difference_days>=0 and difference_days<2 and allow_leave_request==False):
                
                is_compensatory_off = True
                
            #elif (leave_type == 'Compensatory-Off (CO)' and difference_days<0 and allow_leave_request==False):
                
             #   raise osv.except_osv(_('Warning!'),_("You cannot apply for a backdated Compensatory-Off"))
                

            elif (leave_type == 'Maternity Leave (ML)' and date_from<str(date_after_3months_from_current_date) and date_from>=str(current_date_date) and allow_leave_request==False):

                is_maternity_leave = True
                
            elif (leave_type == 'Maternity Leave (ML)' and date_from<str(current_date_date) and allow_leave_request==False):
                
                raise osv.except_osv(_('Warning!'),_("You cannot apply for a backdated Maternity Leave"))
                

            elif (leave_type == 'Privilege Leave (PL)' and difference_days<14 and difference_days>=0 and allow_leave_request==False):
               
               is_optional_item_exists = True
               
            #elif (leave_type == 'Privilege Leave (PL)' and difference_days<0 and allow_leave_request==False):
               
             #  raise osv.except_osv(_('Warning!'),_("You cannot apply for a backdated Privilege Leave"))
               

            else:
            
                for m in self.browse(cr, uid, ids, context=None):
                    business_trip = m.business_trip
            
                search_leave_submit_email_template = self.pool.get('email.template').search(cr,uid,[('model_id.model','=','hr.holidays'),('lang','=','leave submit')], context=context)
            
                #if search_leave_submit_email_template and business_trip == False:
            
                #    send_leave_submit_mail = self.pool.get('email.template').send_mail(cr, uid, search_leave_submit_email_template[0], ids[0], force_send=True, context=context)
                
                for record in self.browse(cr, uid, ids, context=context):
                    print "tttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt", record.id
                    if record.employee_id and record.employee_id.parent_id and record.employee_id.parent_id.user_id:
                        self.message_subscribe_users(cr, uid, [record.id], user_ids=[record.employee_id.parent_id.user_id.id,record.employee_id.hro.id], context=context)        

                return self.write(cr, uid, ids, {'state': 'confirm'})
               
               
                
            
            if(is_optional_item_exists):
               

               
               
               return {
                'type': 'ir.actions.act_window',
                'name': _('Privilege Leave Request Wizard'),
                'res_model': 'leave.request.wizard',
                'res_id': ids[0],
                'view_type': 'form',
                'view_mode': 'form',
               # 'view_id': form_view_id,
                'target': 'new',
                'nodestroy': True,
                }

            elif(is_paternity_leave):

                return {
                'type': 'ir.actions.act_window',
                'name': _('Paternity Leave Request Wizard'),
                'res_model': 'paternity.leave.request.wizard',
                'res_id': ids[0],
                'view_type': 'form',
                'view_mode': 'form',
               # 'view_id': form_view_id,
                'target': 'new',
                'nodestroy': True,
                }            

            elif(is_wedding_leave):

                return {
                'type': 'ir.actions.act_window',
                'name': _('Wedding Leave Request Wizard'),
                'res_model': 'wedding.leave.request.wizard',
                'res_id': ids[0],
                'view_type': 'form',
                'view_mode': 'form',
               # 'view_id': form_view_id,
                'target': 'new',
                'nodestroy': True,
                }

            elif(is_compensatory_off):

                return {
                'type': 'ir.actions.act_window',
                'name': _('Compensatory-Off Request Wizard'),
                'res_model': 'compensatory.leave.request.wizard',
                'res_id': ids[0],
                'view_type': 'form',
                'view_mode': 'form',
               # 'view_id': form_view_id,
                'target': 'new',
                'nodestroy': True,
                }

            elif(is_casual_leave):

                return {
                'type': 'ir.actions.act_window',
                'name': _('Casual Leave Request Wizard'),
                'res_model': 'casual.leave.request.wizard',
                'res_id': ids[0],
                'view_type': 'form',
                'view_mode': 'form',
               # 'view_id': form_view_id,
                'target': 'new',
                'nodestroy': True,
                }


            elif(is_maternity_leave):

                return {
                'type': 'ir.actions.act_window',
                'name': _('Maternity Leave Request Wizard'),
                'res_model': 'maternity.leave.request.wizard',
                'res_id': ids[0],
                'view_type': 'form',
                'view_mode': 'form',
               # 'view_id': form_view_id,
                'target': 'new',
                'nodestroy': True,
                }


            else:
            
                wf_service = netsvc.LocalService('workflow')
                wf_service.trg_validate(uid, 'hr.holidays', ids[0], 'order_confirm', cr)

           
                view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hr_holidays', 'edit_holiday_new')
                view_id = view_ref and view_ref[1] or False,
                
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Leave Requests'),
                    'res_model': 'hr.holidays',
                    'res_id': ids[0],
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': view_id,
                    'target': 'current',
                    'nodestroy': True,
            }
            
            
        
        
        return self.write(cr, uid, ids, {'state': 'confirm'})

    def action_allocation_request_confirm(self,cr,uid,ids,context=None):
        self.write(cr, uid, ids, {'state': 'confirm'})
        return True

    def conversion_of_sick_leave_to_pl(self,cr,uid,ids=None,context=None):
    
        leaves_search = self.pool.get('hr.holidays').search(cr, uid, [('id', '>', 0),('type', '=', 'remove')], context=context)
        
        print leaves_search, "ggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg"
        
        for record in self.browse(cr, uid, leaves_search):
            from time import strftime
            date_from = record.date_from[:10]

            date_from_year = int(date_from[:4])
            date_from_month = int(date_from[5:7])
            date_from_date = int(date_from[8:10])

            from datetime import date
            from dateutil.relativedelta import relativedelta
            
            date_after_7days_from_date_from = date(date_from_year,date_from_month,date_from_date) + relativedelta(days=+7)
            
            

            no_of_days = record.number_of_days_temp

            leave_type = record.holiday_status_id.name
            print no_of_days,leave_type, "sssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss"
            from time import strftime
            today_date = strftime("%Y-%m-%d")

            if (leave_type == 'Sick Leave (SL)' and no_of_days>1):
                if not record.medical_certificate_line:
                    if today_date >= str(date_after_7days_from_date_from):
                        search_pl_leave = self.pool.get('hr.holidays.status').search(cr,uid,[('name','=','Privilege Leave (PL)')], context=context)
                        self.write(cr, uid, ids, {'holiday_status_id': search_pl_leave[0], 'upload_medical_certificate': False})

        return True

    def allocate_sick_leaves_annually(self,cr,uid,ids=None,context=None):
        #self.write(cr, uid, ids, {'state': 'confirm'})

        emp_search = self.pool.get('hr.employee').search(cr, uid, [('id', '>', 0)], context=context)

        
        print emp_search, "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
        for m in self.pool.get('hr.employee').browse(cr, uid, emp_search):
            name = m.name
            

            joining_date = m.join_date

            sick_leaves = m.sick_leaves

            

            joining_date_year = int(joining_date[:4])
            joining_date_month = int(joining_date[5:7])
            joining_date_date = int(joining_date[8:10])


            from dateutil.relativedelta import relativedelta

            import datetime
            from datetime import datetime
            from datetime import timedelta
            from time import strftime
            from datetime import date

            #Getting the date after 3 and 6 months from the date of joining

            date_after_8months = date(joining_date_year,joining_date_month,joining_date_date) + relativedelta(months=+8)
            #date_after_6months = date(joining_date_year,joining_date_month,joining_date_date) + relativedelta(months=+6)

            today_date = strftime("%Y-%m-%d")

            

            search_sick_leave = self.pool.get('hr.holidays.status').search(cr,uid,[('name','=','Sick Leave (SL)')], context=context)

            search_casual_leave = self.pool.get('hr.holidays.status').search(cr,uid,[('name','=','Casual Leave (CL)')], context=context)

            if today_date > str(date_after_8months):
                print "tttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt"
                create_id = self.pool.get('hr.holidays').create(cr, uid, {'name': 'Allocation of 4 SLs annually', 'holiday_status_id': search_sick_leave[0], 'employee_id': m.id, 'number_of_days_temp': 4, 'type': 'add'}, context=context)
               
               
                self.pool.get('hr.holidays').holidays_first_validate(cr, uid, [create_id], context=context)
                #self.pool.get('hr.holidays').holidays_validate(cr, uid, [create_id], context=context)

                
                create_casual_id = self.pool.get('hr.holidays').create(cr, uid, {'name': 'Allocation of 5 CLs annually', 'holiday_status_id': search_casual_leave[0], 'employee_id': m.id, 'number_of_days_temp': 5, 'type': 'add'}, context=context)

                
               
               
                self.pool.get('hr.holidays').holidays_first_validate(cr, uid, [create_casual_id], context=context)
                #self.pool.get('hr.holidays').holidays_validate(cr, uid, [create_casual_id], context=context)

        return True

class reason_refusal(osv.osv):
    _name = "reason.refusal"
    _description = "Reason for Refusal"
    

    _columns = {

        'name':fields.char('Description'),
        'refusal_reason':fields.text('Reason for Refusal'),
        
        

    }

reason_refusal()

class compensatory_leaves(osv.osv):
    _name = "compensatory.leaves"
    _description = "Compensatory Leave Details"
    

    _columns = {

        'compensatory_id':fields.many2one('hr.employee','Compensatory Number'),
        'serial_no':fields.integer('Sr No'),
        'compensatory_date':fields.date('Compensatory Leave Date'),
        'date_against_which_co_taken':fields.date('Date against which CO is taken'),
        'compensatory_expiry_date':fields.date('CO Expiry Date'),
        

    }

compensatory_leaves()

class compensatory_leaves_trips(osv.osv):
    _name = "compensatory.leaves.trips"
    _description = "Compensatory Leave Details"
    

    _columns = {

        'compensatory_trip_id':fields.many2one('hr.employee','Compensatory Trip Number'),
        'serial_no':fields.integer('Sr No'),
        'trip_no':fields.many2one('hr.holidays','Trip No.'),
        'number_of_compensatory_offs': fields.integer('No. of Comp-Offs'),
        'compensatory_date':fields.date('Compensatory Date'),
        'day_of_week':fields.selection([('0', 'Monday'),('1', 'Tuesday'),('2', 'Wednesday'),('3', 'Thursday'),('4', 'Friday'),('5', 'Saturday'),('6', 'Sunday')], 'Day'),
        #'date_against_which_co_taken':fields.date('Date against which CO is taken'),
        #'compensatory_expiry_date':fields.date('CO Expiry Date'),
        

    }

compensatory_leaves_trips()


class travel_policies_rules(osv.osv):
    _name = "travel.policies.rules"
    _description = "Travel Policies"
    

    _columns = {
        'name':fields.char('Name'),
        'travel_policies_for_lodging':fields.one2many('travel.policies.lodging','lodging_id',''),
        'travel_policies_for_boarding':fields.one2many('travel.policies.boarding','boarding_id',''),

    }

travel_policies_rules()


class travel_policies_lodging(osv.osv):
    _name = "travel.policies.lodging"
    _description = "Travel Eligibilities/Policies for Lodging"
    

    _columns = {
    
        'lodging_id':fields.many2one('travel.policies.rules','Lodging No.'),
        'grade':fields.selection([('A1', 'A1'),('B1', 'B1'),('B2', 'B2'),('C1', 'C1'),('C2', 'C2'),('C3', 'C3')], 'Grade'),
        'classification_level': fields.selection([('Metros', 'Metros'),('Tier1', 'Tier1'),('Tier2', 'Tier2'),('Other cities', 'Other cities')], 'Classification Level'),
        #'lodging_boarding':fields.selection([('Lodging', 'Lodging'),('Boarding', 'Boarding')], 'Lodging/Boarding'),
        'expense_low':fields.float('Min. Expense'),
        'expense_high':fields.float('Max. Expense'),
        

    }

travel_policies_lodging()

class travel_policies_boarding(osv.osv):
    _name = "travel.policies.boarding"
    _description = "Travel Eligibilities/Policies for Boarding"
    

    _columns = {

        'boarding_id':fields.many2one('travel.policies.rules','Boarding No.'),
        'grade':fields.selection([('A1', 'A1'),('B1', 'B1'),('B2', 'B2'),('C1', 'C1'),('C2', 'C2'),('C3', 'C3')], 'Grade'),
        'classification_level': fields.selection([('Metros', 'Metros'),('Tier1', 'Tier1'),('Tier2', 'Tier2'),('Other cities', 'Other cities')], 'Classification Level'),
        #'lodging_boarding':fields.selection([('Lodging', 'Lodging'),('Boarding', 'Boarding')], 'Lodging/Boarding'),
        'expense_low':fields.float('Min. Expense'),
        'expense_high':fields.float('Max. Expense'),
        

    }

travel_policies_boarding()

class planned_budget_expenses(osv.osv):
    _name = "planned.budget.expenses"
    _description = "Planned Budget Expenses"
    
    def _amount(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}
        cr.execute("SELECT l.id,COALESCE(SUM(l.unit_amount*l.no_of_days),0) AS amount FROM planned_budget_expenses l WHERE id IN %s GROUP BY l.id ",(tuple(ids),))
        res = dict(cr.fetchall())
        return res
    
    def _employee_get(self, cr, uid, context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            return ids[0]
        return False
        
    def _get_employee_grade(self, cr, uid, context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        for j in self.pool.get('hr.employee').browse(cr, uid, ids):
            grade = j.employee_grade
        if grade:
            return grade
        return False
        
    _columns = {
        'employee_id':fields.many2one('hr.employee', 'Employee'),
        'employee_grade':fields.selection([('A1', 'A1'),('B1', 'B1'),('B2', 'B2'),('C1', 'C1'),('C2', 'C2'),('C3', 'C3')], 'Grade'),
        'planned_budget_id':fields.many2one('hr.holidays','Planned Budget Number'),
        'sr_no':fields.integer('Sr. No.',size=32),
        'source':fields.char('Source'),
        'destination':fields.char('Destination'),
        'description':fields.char('Description',required=True),
        'mode_of_travel': fields.selection([('Air','Air'),('Auto','Auto'),('Bus','Bus'),('Car','Car'),('Train','Train'),('Private Vehicle','Private Vehicle'),('Taxi','Taxi')], "Mode Of Travel"),
        'city':fields.many2one('res.city', 'City'),
        'unit_amount': fields.float('Amount', digits_compute=dp.get_precision('Product Price')),
        'type_of_stay': fields.selection([('Travelling','Travelling'),('Lodging','Lodging (Hotel Accomodation)'),('Boarding','Boarding (Daily Allowance)')], "Type"),   
        'no_of_days': fields.integer('No Of Days'),
        'total_amount': fields.function(_amount, string='Total', digits_compute=dp.get_precision('Account')),
        #'invoice_date': fields.date('Invoice Date'),
        #'invoice_no': fields.char('Invoice No.'),
        'expense_from': fields.date('Expense From Date'),
        'expense_to': fields.date('Expense To Date'),
        #'total_amount': fields.float('Amount', size=64),

    }
    
    _defaults = {
           'employee_id': _employee_get,
           'employee_grade': _get_employee_grade,
    
    }
    
    def _get_number_of_days(self, expense_from, expense_to):
        """Returns a float equals to the timedelta between two dates given as string."""

        from datetime import datetime,date
        import datetime

        

        from datetime import datetime,date
        import datetime

        date_from_year = int(expense_from[:4])
        date_from_month = int(expense_from[5:7])
        date_from_date = int(expense_from[8:10])

        date_to_year = int(expense_to[:4])
        date_to_month = int(expense_to[5:7])
        date_to_date = int(expense_to[8:10])
        
        

        #weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

        from datetime import date, timedelta as td

        d1 = date(date_from_year,date_from_month,date_from_date)
        d2 = date(date_to_year,date_to_month,date_to_date)

        print d1,d2, "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"

        delta = d2 - d1
        
        diff_day = delta.days
        
        print diff_day, "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1"

        return diff_day

    
    def onchange_expense_from(self, cr, uid, ids, expense_to, expense_from, type_of_stay):
        """
        If there are no date set for date_to, automatically set one 8 hours later than
        the date_from.
        Also update the number_of_days.
        """
        # date_to has to be greater than date_from
        if type_of_stay == "Lodging":
            if (expense_from and expense_to) and (expense_from > expense_to):
                raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))
    
            result = {'value': {}}
            
            if (expense_to and expense_from) and (expense_from <= expense_to):
                diff_day = self._get_number_of_days(expense_from, expense_to)
                result['value']['no_of_days'] = int(round(math.floor(diff_day)))
                
                return result
            else:
                result['value']['no_of_days'] = 0
            
                return result
        else:
            if (expense_from and expense_to) and (expense_from > expense_to):
                raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))
    
            result = {'value': {}}
            
            if (expense_to and expense_from) and (expense_from <= expense_to):
                diff_day = self._get_number_of_days(expense_from, expense_to)
                result['value']['no_of_days'] = int(round(math.floor(diff_day))+1)
                
                return result
            else:
                result['value']['no_of_days'] = 0
            
                return result
        
    def onchange_expense_to(self, cr, uid, ids, expense_to, expense_from, type_of_stay):
        """
        Update the number_of_days.
        """

        # date_to has to be greater than date_from
        if type_of_stay == "Lodging":
            if (expense_from and expense_to) and (expense_from > expense_to):
                raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))
    
            result = {'value': {}}
            
            if (expense_to and expense_from) and (expense_from <= expense_to):
                diff_day = self._get_number_of_days(expense_from, expense_to)
                print diff_day, round(math.floor(diff_day))+1, "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
                result['value']['no_of_days'] = int(round(math.floor(diff_day)))
                
                return result
                
            else:
                result['value']['no_of_days'] = 0
    
                return result
        else:
            if (expense_from and expense_to) and (expense_from > expense_to):
                raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))
    
            result = {'value': {}}
            
            if (expense_to and expense_from) and (expense_from <= expense_to):
                diff_day = self._get_number_of_days(expense_from, expense_to)
                print diff_day, round(math.floor(diff_day))+1, "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
                result['value']['no_of_days'] = int(round(math.floor(diff_day))+1)
                
                return result
                
            else:
                result['value']['no_of_days'] = 0
    
                return result
            
            
    def onchange_max_budgetary_amount(self, cr, uid, ids, employee_grade, type_of_stay, city, expense_to, expense_from):
        
        # date_to has to be greater than date_from
        if employee_grade and type_of_stay:
            print city, "ttttttttttttttttttttttttttttttttttttttttttttttttttttt"
            
            if type_of_stay == 'Travelling':
                if city:
                
                    values = {
                        'unit_amount': 0.00,
                
                            }
                            
                else:
                
                     values = {
                        'unit_amount': False,
                
                            }           
                            
                if expense_from and expense_to:
                    print "mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm"
                    if (expense_from and expense_to) and (expense_from > expense_to):
                        raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))
    
                    
            
                    if (expense_to and expense_from) and (expense_from <= expense_to):
                        diff_day = self._get_number_of_days(expense_from, expense_to)
                        
                        no_of_days = int(round(math.floor(diff_day))+1)
                        
                    
            
                        
            
                    values = {
                        'no_of_days': no_of_days
                
                            }
                            
                else:
                    
                    values = {
                         'no_of_days': 0
                    
                        }            
                            
                            
                if city and expense_from and expense_to:   
                    values = {
                        'unit_amount': 0.00,
                        'no_of_days': no_of_days
                
                            }         
                            
            
            if type_of_stay == 'Lodging':
                if city:
                
                    city_id = self.pool.get('res.city').search(cr, uid, [('id', '=', city)])
                    for m in self.pool.get('res.city').browse(cr, uid, city_id):
                        city_name = m.name
                        city_classification_level = m.classification_level
                    print city_name, city_classification_level, ids, employee_grade, type_of_stay, "gggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg"     
                    
                    search_budgetary_amount = self.pool.get('travel.policies.lodging').search(cr, uid, [('grade', '=', employee_grade),('classification_level', '=', city_classification_level)])
                
                    for u in self.pool.get('travel.policies.lodging').browse(cr, uid, search_budgetary_amount):
                        min_expense = u.expense_low
                        max_expense = u.expense_high
                    print min_expense, max_expense, "lllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll"    
            
                    values = {
                        'unit_amount': max_expense,
                
                            }
                            
                elif not city:
                
                    values = {
                        'unit_amount': False,
                
                            }            
                
                if expense_from and expense_to:
                    print "mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm"
                    if (expense_from and expense_to) and (expense_from > expense_to):
                        raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))
    
                    
            
                    if (expense_to and expense_from) and (expense_from <= expense_to):
                        diff_day = self._get_number_of_days(expense_from, expense_to)
                        
                        no_of_days = int(round(math.floor(diff_day)))
                        
                    
            
                        
            
                    values = {
                        'no_of_days': no_of_days
                
                            }
                            
                                        
                            
                if city and expense_from and expense_to:
                    print "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"            
                    values = {
                        'unit_amount': max_expense,
                        'no_of_days': no_of_days
                
                            }
                            
                                        
                
            if type_of_stay == 'Boarding':
                if city:
                
                    city_id = self.pool.get('res.city').search(cr, uid, [('id', '=', city)])
                    for m in self.pool.get('res.city').browse(cr, uid, city_id):
                        city_name = m.name
                        city_classification_level = m.classification_level
                    print city_name, city_classification_level, ids, employee_grade, type_of_stay, "gggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg"     
                
                    search_budgetary_amount_boarding = self.pool.get('travel.policies.boarding').search(cr, uid, [('grade', '=', employee_grade),('classification_level', '=', city_classification_level)])
                
                    for v in self.pool.get('travel.policies.boarding').browse(cr, uid, search_budgetary_amount_boarding):
                        min_expense_boarding = v.expense_low
                        max_expense_boarding = v.expense_high
                    print min_expense_boarding, max_expense_boarding, "lllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll"    
            
                    values = {
                        'unit_amount': max_expense_boarding,
                
                        }
                        
                elif not city:
                
                    values = {
                        'unit_amount': False,
                
                            }        
                
                if expense_from and expense_to:
                    print "mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm"
                    if (expense_from and expense_to) and (expense_from > expense_to):
                        raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))
    
                    
            
                    if (expense_to and expense_from) and (expense_from <= expense_to):
                        diff_day = self._get_number_of_days(expense_from, expense_to)
                        
                        no_of_days = int(round(math.floor(diff_day))+1)
                        
                    
            
                        
            
                    values = {
                        'no_of_days': no_of_days
                
                            }
                
                
                if city and expense_from and expense_to:
                    print "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"            
                    values = {
                        'unit_amount': max_expense_boarding,
                        'no_of_days': no_of_days
                
                            }
                
                
                
                
                #else:
                    
                 #   values = {
                  #      'unit_amount': False,
                
                   #         }
            return {'value' : values}
    
        
planned_budget_expenses()


class gradewise_mode_of_travel_details_budget(osv.osv):
    _name = "gradewise.mode.of.travel.details.budget"
    _description = "Grade-wise Mode of Travel Details for budget"
    

    _columns = {
        
        'travel_id':fields.many2one('hr.holidays','Travel Number'),
        'sr_no':fields.integer('Sr. No.',size=32),
        'grade':fields.selection([('A1', 'A1'),('B1', 'B1'),('B2', 'B2'),('C1', 'C1'),('C2', 'C2'),('C3', 'C3')], 'Grade'),
        'mode_of_travel':fields.text('Mode of Travel'),
        'mode_of_local_conveyance':fields.text('Mode of Local Conveyance'),
        
        

    }

gradewise_mode_of_travel_details_budget()

class travelled_city_details(osv.osv):
    _name = "travelled.city.details"
    _description = "Details of the cities travelled"
    

    _columns = {
        
        'city_id':fields.many2one('hr.holidays','City Number'),
        'sr_no':fields.integer('Sr. No.',size=32),
        #'grade':fields.selection([('A1', 'A1'),('B1', 'B1'),('B2', 'B2'),('C1', 'C1'),('C2', 'C2'),('C3', 'C3')], 'Grade'),
        'city':fields.many2one('res.city','City'),
        #'mode_of_local_conveyance':fields.text('Mode of Local Conveyance'),
        
        

    }

travelled_city_details()


class lodging_expenses_budget(osv.osv):
    _name = "lodging.expenses.budget"
    _description = "Budgetary Range for Lodging Expenses"
    

    _columns = {
        
        'lodging_expenses_id':fields.many2one('hr.holidays','Lodging Expenses Number'),
        'sr_no':fields.integer('Sr. No.',size=32),
        'city':fields.many2one('res.city', 'City'),
        'classification_level': fields.selection([('Metros', 'Metros'),('Tier1', 'Tier1'),('Tier2', 'Tier2'),('Other cities', 'Other cities')], 'Classification Level'),
        'expense_low':fields.float('Min. Expense'),
        'expense_high':fields.float('Max. Expense'),
        
        

    }

lodging_expenses_budget()

class boarding_expenses_budget(osv.osv):
    _name = "boarding.expenses.budget"
    _description = "Budgetary Range for Boarding Expenses"
    

    _columns = {
        
        'boarding_expenses_id':fields.many2one('hr.holidays','Boarding Expenses Number'),
        'sr_no':fields.integer('Sr. No.',size=32),
        'city':fields.many2one('res.city', 'City'),
        'classification_level': fields.selection([('Metros', 'Metros'),('Tier1', 'Tier1'),('Tier2', 'Tier2'),('Other cities', 'Other cities')], 'Classification Level'),
        'expense_low':fields.float('Min. Expense'),
        'expense_high':fields.float('Max. Expense'),
        
        

    }

boarding_expenses_budget()


class gradewise_mode_of_travel_details(osv.osv):
    _name = "gradewise.mode.of.travel.details"
    _description = "Grade-wise Mode of Travel Details"
    

    _columns = {

        'sr_no':fields.integer('Sr. No.',size=32),
        'grade':fields.selection([('A1', 'A1'),('B1', 'B1'),('B2', 'B2'),('C1', 'C1'),('C2', 'C2'),('C3', 'C3')], 'Grade'),
        'mode_of_travel':fields.text('Mode of Travel'),
        'mode_of_local_conveyance':fields.text('Mode of Local Conveyance'),
        
        

    }

gradewise_mode_of_travel_details()

class advance_amount(osv.osv):
    _name = "advance.amount"
    _description = "Provision of Advance Amount"
    

    _columns = {
        'advance_id':fields.many2one('hr.holidays','Advance Amount Number'),
        'sr_no':fields.integer('Sr. No.',size=32),
        'name':fields.char('Description'),
        'date_of_advance':fields.date('Date'),
        'advance_amount':fields.float('Amount'),
        
        
        

    }

advance_amount()

class travel_during_odd_hours(osv.osv):
    _name = "travel.during.odd.hours"
    _description = "Travel during odd hours"
    

    _columns = {
        'odd_hour_id':fields.many2one('hr.holidays','Travel Number'),
        'sr_no':fields.integer('Sr. No.',size=32),
        'source':fields.char('Source'),
        'destination':fields.char('Destination'),
        'city':fields.many2one('res.city','City'),
        'conveyance_amount':fields.float('Conveyance Amount'),
        'mode_of_travel': fields.selection([('Air','Air'),('Auto','Auto'),('Bus','Bus'),('Car','Car'),('Train','Train'),('Private Vehicle','Private Vehicle'),('Taxi','Taxi')], "Mode Of Travel"),
        'from_travel':fields.datetime('From'),
        'to_travel':fields.datetime('To'),
       
        
        
        

    }

travel_during_odd_hours()


#---------------------------------------------------------------------
#Inherited the View for the Auth SIgn Up for the Link given by shreyas
#---------------------------------------------------------------------


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
