
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
from datetime import datetime,date,timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from bsddb.dbtables import _columns

blood_group_selection = [
    ('a+', 'A+'),
    ('a-', 'A-'),
    ('b+', 'B+'),
    ('b-', 'B-'),
    ('ab+', 'AB+'),
    ('ab-', 'AB-'),
    ('o+', 'O+'),
    ('o-', 'O-'),
]

class res_partner_bank(osv.osv):
    _inherit = 'res.partner.bank'
    
    def _bank_type_get(self, cr, uid, context=None):
        bank_type_obj = self.pool.get('res.partner.bank.type')

        result = []
        type_ids = bank_type_obj.search(cr, uid, [])
        bank_types = bank_type_obj.browse(cr, uid, type_ids, context=context)
        for bank_type in bank_types:
            result.append((bank_type.code, bank_type.name))
        return result
    
    
    
    _columns = {
    
    'state': fields.selection(_bank_type_get, 'Bank Account Type',
            change_default=True),
            
    'partner_id': fields.many2one('res.partner', 'Account Owner',
            ondelete='cascade', select=True),
    'bank_ifsc_code': fields.char('Bank IFSC Code'),
    'bank_account_id': fields.many2one('res.partner.bank', 'Bank Account Number'),  
    }


class hr_employee(osv.osv):
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    
    
    def copy(self, cr, uid, id, default=None, context=None):

        if not default:
            default = {}
        default.update({
            'auto_emp_code': self.pool.get('ir.sequence').get(cr, uid, 'hr.employee'),

        })
        return super(hr_employee, self).copy(cr, uid, id, default, context=context)
    
    def _calculate_age(self, cr, uid, ids, birthday, arg, context=None):

        res = dict.fromkeys(ids, False)
        for ee in self.browse(cr, uid, ids, context=context):
            if ee.birthday:
                dBday = datetime.strptime(ee.birthday, OE_DFORMAT).date()
                dToday = datetime.now().date()
                res[ee.id] = (dToday - dBday).days / 365
        return res
        
    def _compute_emp_code(self, cr, uid, ids, fields, arg, context=None):
        res = {}
        for statement in self.browse(cr, uid, ids, context=context):
            res[statement.id] = statement.auto_emp_code

        return res

    _columns = {
        
        'same_as_above':fields.boolean('Same As Above'),
        'auto_emp_code': fields.char('Employee Code', size=64),
        'auto_emp_code_same': fields.function(_compute_emp_code, string='Employee Code',type="char"),
        'home_address_new': fields.text('Home Address'),
        'permanent_address_new': fields.text('Permanent Address'),
        'blood_group': fields.selection(blood_group_selection, 'Blood Group', help='Blood Group Of The Employee'),
        'age': fields.function(_calculate_age, type='integer', method=True, string='Age'),
        'no_of_dependents': fields.integer(string='No Of Dependents'),
        'pan_card_no': fields.char('PAN Card No.'), 
        'emergency_contact': fields.char('Emergency Contact Person', help="Name of the Emergency contact Person"),
        'permanent_address': fields.many2one('res.partner', 'Permanent Address', domain="[('name','=','abcd')]"),
        'personal_emailid': fields.char('Personal Email ID', size=240),
        'relation': fields.char('Relation', help='Relation with Employee'),
        'emergency_phone': fields.char('Emergency Phone', size = 12, help='Emergency Phone Number'),
        'employee_id': fields.many2one('hr.employee', 'Employee'),
    }
    
    _defaults = {
        'auto_emp_code': lambda obj, cr, uid, context: '/',

    }
    _sql_constraints = [
        ('name_auto_emp_code_uniq', 'unique(auto_emp_code, company_id)', 'Employee Code must be unique per Company!'),

    ]
    
    def onchange_same_as_above(self,cr, uid, ids,same_as_above,home_address_new,context=None):
        value={}
        if same_as_above and home_address_new:
            if same_as_above == True:            
                value = {'permanent_address_new':home_address_new}

        else:

                value = {'permanent_address_new':''}
        
        return {'value':value}
    
    def create(self, cr, uid, vals, context=None):
        name = vals['name']
        img = vals['image_medium']
        department_id = vals['department_id']
        join_date = vals['join_date']
        extension = vals['extension']
        work_email = vals['work_email']
        job = vals['job_id']
        search_dept = self.pool.get('hr.department').search(cr,uid,[('id','=',department_id)], context=context)
        
        for g in self.pool.get('hr.department').browse(cr,uid,search_dept):
            dept_code = g.code
            dept_name = g.name
       
        
        if dept_name in ('Directors','Human Resources & Administration','Sales', 'Marketing','Accounts & Finance','ERP Department','Shipping & Distribution','Artwork & Development','Sales & Marketing Support'):

            
            search_sequence_record = self.pool.get('ir.sequence').search(cr,uid,[('code','=','hr.employee')], context=context)
            
            
            write_dept_code = self.pool.get('ir.sequence').write(cr, uid, search_sequence_record, {'prefix': dept_code})
            
        
        
        if vals.get('auto_emp_code','/')=='/':
            vals['auto_emp_code'] = self.pool.get('ir.sequence').get(cr, uid, 'hr.employee') or '/'
            
        create_id = self.pool.get('hr.employee.new').create(cr, uid, {'department_id': department_id , 'name': name, 'emp_code':vals['auto_emp_code'],'join_date': join_date, 'image_new': img,'work_email':work_email,'job_id':job,'extension':extension}, context=context)    
            
        employee_id_created = super(hr_employee, self).create(cr, uid, vals, context=context)
        
        search_template = self.pool.get('email.template').search(cr,uid,[('model_id.model','=','hr.employee'),('lang','=','welcome to employee')], context=context)
        
        
        if search_template:
            
                send_welcome_mail = self.pool.get('email.template').send_mail(cr, uid, search_template[0], employee_id_created, force_send=True, context=context)
        
        return employee_id_created
    
    
    def birthday_reminder(self, cr, uid, ids=None, context=None):
        emp_search = self.pool.get('hr.employee').search(cr, uid, [('id', '>', 0)], context=context)

        
        for record in self.pool.get('hr.employee').browse(cr, uid, emp_search):
            count = 0
            emp_active = record.active
            birth_date = record.birthday

            if record.name not in('Administrator','Nitin Butani','Akshay Butani','Prakash Butani') and emp_active == True and birth_date:
                
                emp_record_id = record.id
                emp_work_mail = record.work_email
                today = datetime.now()
                today_day = today.day
                today_month = today.month

                birth_date_month = int(birth_date[5:7])
                birth_date_day = int(birth_date[8:10])

                if today_day == birth_date_day and today_month == birth_date_month:
                    search_template = self.pool.get('email.template').search(cr,uid,[('model_id.model','=','hr.employee'),('lang','=','Birthday Reminder')], context=context)

                    if search_template:

                        self.pool.get('email.template').send_mail(cr, uid, search_template[0], emp_record_id, force_send=True, context=context)
                        count = count+1

        return True
        
class hr_department(osv.osv):

    _inherit = 'hr.department'
    
    _columns = {
        'code': fields.char('Code'),
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


