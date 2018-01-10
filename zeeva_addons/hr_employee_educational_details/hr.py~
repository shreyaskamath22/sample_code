

from openerp.osv import  fields, osv


EDUCATION_SELECTION = [
    ('ssc', 'SSC'),
    ('hsc', 'HSC'),
    ('diploma', 'Diploma'),
    ('degree1', 'Bachelor Degree'),
    ('masters', 'Masters Degree'),
    ('phd', 'PhD'),
]


class hr_history(osv.osv):
    _name = 'hr.employee.history'
    _description = "Employee's Previous Job History"
    
    _columns = {
        'company': fields.char('Company Name'),
        'designation': fields.char('Designation'),
        'address': fields.char('Address'),
        'contact': fields.char('Contact'),
        'total_exp': fields.char('Total Experience'),
        'employee_id': fields.many2one('hr.employee', 'Employee'),       
    }

class hr_skills(osv.osv):

    _name = 'hr.employee.skills'
    _description = 'HR Employee Skills'

    _columns = {
        'name': fields.char('Skill',size=100),
        #'employee_id': fields.many2one('hr.employee', 'Employee'),
    }

class hr_edu(osv.osv):

    _name = 'hr.employee.edu'
    _description = 'HR Employee Education'

    _columns = {
        'school_university': fields.char('School/University'),
        'qualification': fields.char('Qualification'),
        'level': fields.selection(EDUCATION_SELECTION, 'Education'),
        'employee_id': fields.many2one('hr.employee', 'Employee'),
        'year_of_passing': fields.char('Year Of Passing'),
        'class_percentage': fields.char('Class/Percentage'),
        'skill_id': fields.many2many('hr.employee.skills', 'edu_skills_rel', 'edu_id', 'skills', string="Key Skills"),
        'major_subjects': fields.char('Major/Optional Subjects'),
    }
    


class hr_employee(osv.osv):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    _columns = {
        'job_employee_id': fields.one2many('hr.employee.history', 'employee_id', 'History'),
        'edu_employee_id': fields.one2many('hr.employee.edu', 'employee_id', 'Education'),
    }
