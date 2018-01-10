import datetime
import time
from itertools import groupby
from operator import itemgetter

import math
from openerp import netsvc
from openerp import tools
from openerp.addons.base_status.base_stage import base_stage
from openerp.osv import fields, osv
from openerp.tools.translate import _
from bzrlib.transport import readonly

import random
from urllib import urlencode
from urlparse import urljoin
from dateutil.relativedelta import relativedelta

import datetime
from datetime import datetime
from datetime import timedelta
from time import strftime
from datetime import date

class hr_employee_points(osv.osv):

    _name = 'hr.employee.points'
    _description = 'HR Employee points'
    

    _columns = {
        'sr_no': fields.integer('Sr. No.'),
        'remarks': fields.char('Remarks', size=256),
        'rating': fields.selection([('1', '1'), ('2', '2'),('3', '3'), ('4', '4'),('5','5')], 'Rating'),
        'point_id': fields.many2one('hr.employee.confirmation', 'Confirmation'),
    }
    
#     _defaults = {
#         "point_id": lambda self, cr, uid, c: c.get('point_id', False),
#     }

class hr_employee_confirmation(osv.osv):
    _name = 'hr.employee.confirmation'
    
    _inherit = ["mail.thread"]
    
    def _employee_get(self, cr, uid, ids, context=None):        
        ids_p = self.pool.get('hr.employee').search(cr, uid, [('parent_id.user_id','=',uid)], context=context)
        emp_list = []
        for empl in self.pool.get('hr.employee').browse(cr, uid, ids_p):
            emp_id = empl.id
            emp_list.append('')
            emp_list.append(emp_id)
            print empl.name
            return emp_list
    

    def _get_url(self, cr, uid, ids, action='login', view_type=None, menu_id=None, res_id=None, model=None, context=None):
        """ generate a signup url for the given partner ids and action, possibly overriding
            the url state components (menu_id, id, view_type) """
        res = dict.fromkeys(ids, False)
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        for partner in self.browse(cr, uid, ids, context):
            # when required, make sure the partner has a valid signup token
            if context and context.get('signup_valid') and not partner.user_ids:
                self.signup_prepare(cr, uid, [partner.id], context=context)
                partner.refresh()

            # the parameters to encode for the query and fragment part of url
            query = {'db': cr.dbname}
            

            
            

            res[partner.id] = urljoin(base_url, "?%s" % (urlencode(query)))

        return res
    
    
    _columns = {
            'company_id': fields.many2one('res.company', 'Company'),
            'salutation': fields.selection([('Mr', 'Mr.'),('Ms', 'Ms.'),('Mrs', 'Mrs.')], 'Salutation'),
            'on_hold_till_date':fields.date('On Hold Till'),
            'current_user':fields.many2one('res.users','Current User',size=32),
            'name': fields.many2one('hr.employee', "Employee Name", required=True, domain="['|',('hro','=',uid),'|',('parent_id.parent_id.user_id','=',uid),('parent_id.user_id','=',uid)]"),
            'identification_id': fields.char('Employee Code'),
            'department_id': fields.many2one('hr.department', "Department", required=True),
            'join_date': fields.date("Date Of Joining"),
            'job_id': fields.many2one('hr.job', 'Designation', required=True),
            'gender': fields.many2one('hr.employee','Gender'),
            'marital': fields.many2one('hr.employee','Marital'),
            'review_by': fields.many2one('hr.employee','Review Completed By', domain="[('manager', '=', True)]"),
            'manager_id': fields.many2one('hr.employee', 'Manager', required=True, domain="[('manager', '=', True)]"),
            'points_ids': fields.one2many('hr.employee.points', 'point_id', 'Confirmation Points'),
            'state': fields.selection([('Draft', 'Draft'),('Submitted to Mgmt', 'Submitted to Reporting Manager'),('On Hold', 'On Hold'),('Confirmed by Mgmt', 'Confirmed by Reporting Manager'),('Confirmation validated by HRO', 'Confirmation validated by HRO'),('Warning', 'Warning'),('Terminated', 'Terminated')], 'Status'),    
            'date_of_confirmation': fields.date("Date Of Confirmation"),
            'emp_status': fields.boolean('Active'),
            'date_of_leaving': fields.date("Date Of Leaving"),
            'signup_url': fields.function(_get_url,type='char',string='Signup URL'),
	    'flag': fields.boolean('Flag'),
    }
    
    _rec_name = 'name'
    _order = "name"

    _sql_constraints = [
        ('name_unique12', 'UNIQUE(name)', 'This Employee is already in process of confirmation !'),
    ]
    
    _defaults = {
       # "points_ids": _points_default,
        "state": 'Draft',
        'name': _employee_get,
        'current_user': lambda obj, cr, uid, ctx=None: uid,
	'flag': False,
	    'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'hr.employee.confirmation', context=c),
    }
    
    
    def display_rating_points_for_employee(self, cr, uid, ids, context=None):
        print "tttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt"
        for x in self.browse(cr, uid, ids, context=None):
            form_id = x.id
            print form_id, "-------------------------------------------------------"
            
            cr.execute('delete from hr_employee_points where point_id=%s',([form_id]))
            
            create_id_1 = self.pool.get('hr.employee.points').create(cr, uid, {'sr_no': 1,'remarks': 'Has shown Improvement in work and is a quick learner', 'rating': '','point_id': form_id}, context=context)
            
            create_id_2 = self.pool.get('hr.employee.points').create(cr, uid, {'sr_no': 2,'remarks': 'Is Friendly, co-operative, communicates well and is a team player', 'rating': '','point_id': form_id}, context=context)
            
            create_id_3 = self.pool.get('hr.employee.points').create(cr, uid, {'sr_no': 3,'remarks': 'Wants to know and learn new things and is enthusiastic about work', 'rating': '','point_id': form_id}, context=context)
            
            create_id_4 = self.pool.get('hr.employee.points').create(cr, uid, {'sr_no': 4,'remarks': 'Keen to get new responsibilities and has the ability to handle it', 'rating': '','point_id': form_id}, context=context)
            
            create_id_5 = self.pool.get('hr.employee.points').create(cr, uid, {'sr_no': 5,'remarks': 'Is punctual, disciplined and polite in behaviour', 'rating': '','point_id': form_id}, context=context)
            
            create_id_6 = self.pool.get('hr.employee.points').create(cr, uid, {'sr_no': 6,'remarks': 'Maintains good relation with other department and co-ordinates among them well', 'rating': '','point_id': form_id}, context=context)
            
            
            #res = cr.fetchall()
            #print res, "mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm"
            #cr.execute('update hr_employee_points set point_id = %s group by remarks', [form_id])
        self.write(cr, uid, ids, {'flag': True})
    
    def onchange_date_of_joining(self, cr, uid, ids, name, context=None):
        value = {'join_date': False,'department_id': False, 'job_id': False, 'gender': False, 'marital': False, 'manager_id': False,'salutation': False, 'date_of_confirmation': False, 'date_of_leaving': False }
        if name:
            emp = self.pool.get('hr.employee').browse(cr, uid, name)
            value['join_date'] = emp.join_date
            value['department_id'] = emp.department_id.id
            value['job_id'] = emp.job_id.id
            value['identification_id'] = emp.auto_emp_code
            value['gender'] = emp.gender
            value['marital'] = emp.marital               
            value['manager_id'] = emp.parent_id.id
            value['date_of_leaving'] = emp.relieving_date
            value['emp_status'] = emp.active
            print value['date_of_leaving']
            joining_date_year = int( emp.join_date[:4])
            joining_date_month = int( emp.join_date[5:7])
            joining_date_date = int( emp.join_date[8:10])
            date_after_3months = date(joining_date_year,joining_date_month,joining_date_date) + relativedelta(months=+3)
            value['date_of_confirmation'] = str(date_after_3months)
            if value['gender'] == "male":
                value['salutation'] = "Mr"
            elif value['gender'] == "female" and value['marital'] == "single":
                value['salutation'] = "Ms"
            elif value['gender'] == "female" and value['marital'] == "married":
                value['salutation'] = "Mrs"
        return {'value': value}
    
    def action_employee_confirm(self, cr, uid, ids, context=None):
        for x in self.browse(cr, uid, ids, context=None):
            query = {'db': cr.dbname}
            
            nm = x.name.name
            iddd = x.name.id
            joindate = x.join_date
            dateOfConf = x.date_of_confirmation
            url = x.signup_url
            points_id = x.points_ids
            joining_date_year = int( x.join_date[:4])
            joining_date_month = int(x.join_date[5:7])
            joining_date_date = int( x.join_date[8:10])
            con_date_year = int( x.date_of_confirmation[:4])
            con_date_month = int(x.date_of_confirmation[5:7])
            con_date_date = int( x.date_of_confirmation[8:10])
            jd_date = str(date(joining_date_year,joining_date_month,joining_date_date))
            conDate = str(date(con_date_year,con_date_month,con_date_date))
            date_after_3months = str(date(joining_date_year,joining_date_month,joining_date_date) + relativedelta(months=+3))
            date_after_6months = str(date(joining_date_year,joining_date_month,joining_date_date) + relativedelta(months=+6))
            if (conDate < jd_date) or (conDate < date_after_3months):
                raise osv.except_osv(_('Warning!'),_("Please Select Appropriate Date"))
            if not points_id:
                raise osv.except_osv(_('Warning!'),_("Please click on 'Display' and rate the Employee's performance during his probationary period on a scale of 1 to 5 then click on 'Submit'."))
            
            if x.name.parent_id and x.name.parent_id.user_id:
                self.message_subscribe_users(cr, uid, [x.id], user_ids=[x.name.parent_id.user_id.id,x.name.hro.id,52], context=context)
        
        search_rating_details = self.pool.get('hr.employee.points').search(cr, uid, [('point_id', '=', ids[0])])
        count = 0
        for t in self.pool.get('hr.employee.points').browse(cr, uid, search_rating_details):
                rating = t.rating
               
                print t.rating, 'Value of tttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt'

                count = count+1
                if not rating:
                    raise osv.except_osv(_('Warning!'),_("Please give the rating for point no %s")%(count))
       
        emp_user_id = iddd
        
        if uid == emp_user_id:
            raise osv.except_osv(_('Warning!'),_('You cannot validate your own confirmation')) 
        message = _("<b>Employee confirmation for %s : Submitted to Reporting Manager</b>") % (nm)
        self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)
        return self.write(cr, uid, ids, {'on_hold_till_date': date_after_6months, 'state': 'Submitted to Mgmt'})

    
    ''' This is a scheduler function when on hold till date reaches the todays date'''
    def action_employee_tobe_confirm(self, cr, uid, ids=None, context=None):
        emp_conf = self.pool.get('hr.employee.confirmation').search(cr, uid, [('id', '>', 0)], context=None)

        for x in self.pool.get('hr.employee.confirmation').browse(cr, uid, emp_conf):
            emp_active = x.name.active
            form_id = x.id
            c_status = x.state
            hold_date = x.on_hold_till_date
                    
            hold_date_year = int(hold_date[:4])
            hold_date_month = int(hold_date[5:7])
            hold_date_date = int(hold_date[8:10])
            print emp_active
            if emp_active == True:                
                if c_status == "On Hold":
                    date_hd = date(hold_date_year,hold_date_month,hold_date_date)
                    today_date = strftime("%Y-%m-%d")
                    if str(date_hd) < str(today_date):
                        raise osv.except_osv(_('Warning!'),_('On hold Till Date Cannot be Less than Todays Date'))
                    if today_date == str(date_hd) and c_status == "On Hold":
                        search_template = self.pool.get('email.template').search(cr,uid,[('model_id.model','=','hr.employee.confirmation'),('lang','=','pending confirmation')], context=context)
                        if search_template:
                            send_employee_confirmation_mail = self.pool.get('email.template').send_mail(cr, uid, search_template[0], form_id, force_send=True, context=context)
                    
                    return True
    
    def print_confirmation_letter(self, cr, uid, ids, context=None):
        
        #assert len(ids) == 1, 'This option should only be used for a single id at a time'
        #wf_service = netsvc.LocalService("workflow")
        #wf_service.trg_validate(uid, 'hr.employee.confirmation', ids[0], 'quotation_sent', cr)
        for x in self.browse(cr, uid, ids, context=context):
            joindate = x.join_date
            dateOfConf = x.date_of_confirmation
        datas = {
                 'model': 'hr.employee.confirmation',
                 'ids': ids,
                 'form': self.read(cr, uid, ids[0], context=context),
                 'date_of_confirmation': dateOfConf,
        }
        print datas
        return {'type': 'ir.actions.report.xml', 'report_name': 'hr.employee.confirmation', 'datas': datas, 'nodestroy': True}

    
    def action_employee_confirm_by_mgmt(self, cr, uid, ids, context=None):
        '''search_template = self.pool.get('email.template').search(cr,uid,[('model_id.model','=','hr.employee.confirmation'),('lang','=','confirmation from mgmt')], context=context)
        if search_template:
            print "ggggggggggggggggggggggggggggggggggggggggggggggg", search_template
            send_employee_confirmation_mail = self.pool.get('email.template').send_mail(cr, uid, search_template[0], ids[0], force_send=True, context=context)
        '''
        for x in self.browse(cr, uid, ids, context=None):
            
            nm = x.name.name
        message = _("<b>Employee confirmation for %s : Confirmed by Reporting Manager, Waiting HRO Validation.</b>") % (nm)
        self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)
        return self.write(cr, uid, ids, {'state': 'Confirmed by Mgmt'})

    def action_employee_reject_by_mgmt(self, cr, uid, ids, name, context=None):
        for x in self.browse(cr, uid, ids, context=None):
            nm = x.name.name
            hold_date = x.on_hold_till_date
            if not hold_date:
                raise osv.except_osv(_('Warning!'),_('Please Select On Hold Till Date'))
                
            else:    
                print hold_date, "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
                
                hold_date_year = int(hold_date[:4])
                hold_date_month = int(hold_date[5:7])
                hold_date_date = int(hold_date[8:10])
    
    
                from dateutil.relativedelta import relativedelta
    
                import datetime
                from datetime import datetime
                from datetime import timedelta
                from time import strftime
                from datetime import date
    
                date_hd = date(hold_date_year,hold_date_month,hold_date_date)
                today_date = strftime("%Y-%m-%d")
                if str(date_hd) < str(today_date):
                    raise osv.except_osv(_('Warning!'),_('On hold Till Date Cannot be Less than Todays Date'))
                '''search_template = self.pool.get('email.template').search(cr,uid,[('model_id.model','=','hr.employee.confirmation'),('lang','=','confirmation rejected')], context=context)
                if search_template:
                    print "ggggggggggggggggggggggggggggggggggggggggggggggg", search_template
                    send_employee_confirmation_mail = self.pool.get('email.template').send_mail(cr, uid, search_template[0], ids[0], force_send=True, context=context)
                  '''
          
            message = _("<b>Employee confirmation for %s : has been kept On Hold.</b>") % (nm)
            self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)
            return self.write(cr, uid, ids, {'state': 'On Hold'})

    def action_employee_warn(self, cr, uid, ids, context=None):
        for x in self.browse(cr, uid, ids, context=None):
            nm = x.name.name
            hold_date = x.on_hold_till_date
            print hold_date, "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
            
            hold_date_year = int(hold_date[:4])
            hold_date_month = int(hold_date[5:7])
            hold_date_date = int(hold_date[8:10])


            from dateutil.relativedelta import relativedelta

            import datetime
            from datetime import datetime
            from datetime import timedelta
            from time import strftime
            from datetime import date

            date_hd = date(hold_date_year,hold_date_month,hold_date_date)
            today_date = strftime("%Y-%m-%d")
            if str(date_hd) < str(today_date):
                raise osv.except_osv(_('Warning!'),_('On hold Till Date Cannot be Less than Todays Date'))
        message = _("<b>Employee confirmation for %s : warning has been given to the Employee.</b>") % (nm)
        self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)        
        return self.write(cr, uid, ids, {'state': 'Warning'})

    def action_employee_confirm_in_warning(self, cr, uid, ids, context=None):
        
                
        return self.write(cr, uid, ids, {'state': 'Submitted to Mgmt'})

    def action_employee_terminate(self, cr, uid, ids, context=None):
        for x in self.browse(cr, uid, ids, context=None):
            hold_date = x.on_hold_till_date
            print hold_date, "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
            
            hold_date_year = int(hold_date[:4])
            hold_date_month = int(hold_date[5:7])
            hold_date_date = int(hold_date[8:10])


            from dateutil.relativedelta import relativedelta

            import datetime
            from datetime import datetime
            from datetime import timedelta
            from time import strftime
            from datetime import date

            date_hd = date(hold_date_year,hold_date_month,hold_date_date)
            today_date = strftime("%Y-%m-%d")
            if str(date_hd) < str(today_date):
                raise osv.except_osv(_('Warning!'),_('On hold Till Date Cannot be Less than Todays Date'))
        for x in self.browse(cr, uid, ids, context=None):
            emp_id = x.name.id
            emp_name = x.name.name
            emp_status = x.name.active
            emp_identification_id = x.name.identification_id
            print emp_name, "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
        search_emp_record = self.pool.get('hr.employee').search(cr,uid,[('name','=',emp_name),('identification_id','=',emp_identification_id)], context=context)
        print search_emp_record, "nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn"
        self.pool.get('hr.employee').write(cr, uid, search_emp_record, {'active': False})      
        message = _("<b>Employee confirmation for %s : Employee has been Terminated.</b>") % (emp_name)
        self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)  
        return self.write(cr, uid, ids, {'state': 'Terminated'})

    def action_confirm_validate(self, cr, uid, ids, context=None):
        search_template = self.pool.get('email.template').search(cr,uid,[('model_id.model','=','hr.employee.confirmation'),('lang','=','Employment Confirmed')], context=context)
        if search_template:
            print "ggggggggggggggggggggggggggggggggggggggggggggggg", search_template
            send_employee_confirmation_mail = self.pool.get('email.template').send_mail(cr, uid, search_template[0], ids[0], force_send=True, context=context)
        for x in self.browse(cr, uid, ids, context=None):
            emp_name = x.name.name
            emp_identification_id = x.name.identification_id
            print emp_name, "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
            search_emp_record = self.pool.get('hr.employee').search(cr,uid,[('name','=',emp_name),('identification_id','=',emp_identification_id)], context=context)
            for h in self.browse(cr,uid,search_emp_record):
                self.pool.get('hr.employee').write(cr, uid, h.id, {'status_of_confirmation': 'Confirmed'})
            for x in self.browse(cr, uid, ids, context=None):
                nm = x.name.name
            message = _("<b>Employee confirmation for %s : Confirmation Validated by HRO.</b>") % (nm)
            self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)       
        return self.write(cr, uid, ids, {'state': 'Confirmation validated by HRO'})
    
    def draft(self, cr, uid, ids, context=None):
        for x in self.browse(cr, uid, ids, context=None):
            
            nm = x.name.name
        message = _("<b>Employee confirmation for %s : Reset To Draft State.</b>") % (nm)
        self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)
        return self.write(cr, uid, ids, {'state': 'Draft'}, context=context)
    
    def action_employee_approved(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'approved'})
    
    
    def send_notification_of_tenure_completion(self, cr, uid, ids=None, context=None):
        emp_search = self.pool.get('hr.employee').search(cr, uid, [('id', '>', 0)], context=context)
        print emp_search
        for m in self.pool.get('hr.employee').browse(cr, uid, emp_search):
            emp_active = m.active
            form_id = m.id
            name = m.name
            joining_date = m.join_date
            joining_date_year = int(joining_date[:4])
            joining_date_month = int(joining_date[5:7])
            joining_date_date = int(joining_date[8:10])
            
            #Getting the date after 3 and 6 months from the date of joining
            if emp_active == True:
                date_after_3months = date(joining_date_year,joining_date_month,joining_date_date) + relativedelta(months=+3)
                date_after_12months = date(joining_date_year,joining_date_month,joining_date_date) + relativedelta(months=+12)
    
                today_date = strftime("%Y-%m-%d")
                print today_date
                if today_date == str(date_after_3months):
                    search_template = self.pool.get('email.template').search(cr,uid,[('model_id.model','=','hr.employee'),('lang','=','Probation period completion')], context=context)
                    if search_template:
                       
                        send_employee_confirmation_mail = self.pool.get('email.template').send_mail(cr, uid, search_template[0], form_id, force_send=True, context=context)
                        
                if today_date == str(date_after_12months):
                    search_template = self.pool.get('email.template').search(cr,uid,[('model_id.model','=','hr.employee'),('lang','=','one year completion')], context=context)
                    if search_template:
                        
                        send_employee_confirmation_mail = self.pool.get('email.template').send_mail(cr, uid, search_template[0], form_id, force_send=True, context=context)
                    print send_employee_confirmation_mail     
        return True

    
