from openerp.osv import fields, osv
import time
import datetime
from datetime import date
from time import strftime
from dateutil.relativedelta import relativedelta
import math
from openerp import SUPERUSER_ID, netsvc
from openerp import netsvc
from openerp import tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from bsddb.dbtables import _columns
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.addons.email_template.html2text import html2text
#from libxml2 import defaultSAXHandlerInit
#from boto.gs.acl import DOMAIN



class hr_expense_expense(osv.osv):

    _name = "hr.expense.expense"
    _inherit = ['hr.expense.expense','mail.thread']
    _description = "Expense"
    _track = {
        'state': {
            'hr_expenses_custom.mt_expense_submitted': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'Waiting Manager Approval',
            'hr_expenses_custom.mt_payment_received': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'paid',
            'hr_expenses_custom.mt_expense_refused': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancelled',
            'hr_expenses_custom.mt_expense_confirmed_by_mgmt': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'Approved By Mgmt',
            'hr_expenses_custom.mt_expense_confirmed_by_manager': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'Waiting Accounts Approval',
            'hr_expenses_custom.mt_expense_confirmed_by_accounts': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'Waiting Mgmt Approval',
        },
    }
    
    def _amount(self, cr, uid, ids, field_name, arg, context=None):
        res= {}
        count = 0
        for expense in self.browse(cr, uid, ids, context=context):
            total = 0.0            
            for line in expense.line_ids:
                total += line.total_amount
                print total
            res[expense.id] = total
        return res
    
    '''def _amount(self, cr, uid, ids, field_name, arg, context=None):
        res= {}
        count = 0
        for expense in self.browse(cr, uid, ids, context=context):
            total = 0.0            
            for line in expense.line_ids:
                total += line.unit_amount * line.no_of_days
                print total
            res[expense.id] = total
        return res'''
    
    def _totalExcess_amount(self, cr, uid, ids, field_name, arg, context=None):
        res= {}
        for expense in self.browse(cr, uid, ids, context=context):
            total = 0.0
            for line in expense.line_ids:
                total += line.diff_in_amount * line.no_of_days
            res[expense.id] = total
        return res

	'''def _total_budget_amount(self, cr, uid, ids, field_name, arg, context=None):
		res= {}
		for expense in self.browse(cr, uid, ids, context=context):
			total = 0.0
			for line in expense.line_ids:
				total += line.total_budget
			res[expense.id] = total
		return res'''
    
    def _planned_amount(self, cr, uid, ids, field_name, arg, context=None):
    	print "gggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg"
        res= {}
        for expense in self.browse(cr, uid, ids, context=context):
            total = 0.0
            for line in expense.planned_ids:
                total += line.total_amount
            res[expense.id] = total
        return res
    
    def _daily_amount(self, cr, uid, ids, field_name, arg, context=None):
        res= {}
        for expense in self.browse(cr, uid, ids, context=context):
            total = 0.0
            for line in expense.daily_ids:
                total += line.unit_amount * line.unit_quantity
            res[expense.id] = total
        return res
    
    def _disallowed_amount(self, cr, uid, ids, field_name, arg, context=None):
        res= {}
        for expense in self.browse(cr, uid, ids, context=context):
            total = 0.0
            for line in expense.daily_ids:
                total += line.disallowed_amount
            res[expense.id] = total
        return res
    
    def _advance_paid(self, cr, uid, ids, field_name, arg, context=None):
        res= {}
        for expense in self.browse(cr, uid, ids, context=context):

            total = expense.advance_paid 
            res[expense.id] = total
        return res
    
    def _net_amount(self, cr, uid, ids, field_name, arg, context=None):
        res= {}
        for expense in self.browse(cr, uid, ids, context=context):
            total = 0.0
            for line in expense.daily_ids:
                total += line.unit_amount - line.disallowed_amount
            res[expense.id] = (total - expense.daily_disallowed_amount - expense.advance_paid)
        return res
    
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'exp_no': self.pool.get('ir.sequence').get(cr, uid, 'hr.employee.confirmation'),
            'exp_no1': self.pool.get('ir.sequence').get(cr, uid, 'hr.expense.expense'),
            
        })
        return super(hr_expense_expense, self).copy(cr, uid, id, default, context=context)
        
    def _payable_amount(self, cr, uid, ids, field_name, arg, context=None):
        res= {}
        for expense in self.browse(cr, uid, ids, context=context):
            total = 0.0
            for line in expense.line_ids:
                total += line.total_amount 
            res[expense.id] = (total - expense.total_disallowed_amount) - expense.total_advance_amount
        return res 

    def total_budget_amount(self, cr, uid, ids, field_name, arg, context=None):
	res= {}
	for expense in self.browse(cr, uid, ids, context=context):
            total = 0.0
	    for line in expense.line_ids:
		total += line.total_budget
	    res[expense.id] = total
        return res
    
    
    _columns = {
    	'computed':fields.boolean('Computed'),
    	'total_disallowed_amount':fields.float('Disallowed Amount'),
        'total_advance_amount':fields.float('Advance Paid'),
        'payable_amount':fields.function(_payable_amount, string='Payable Amount', store=True),
        'exp_no': fields.char('Voucher No.'),
        'exp_no1': fields.char('Voucher No.'),
        'current_user':fields.many2one('res.users','Current User',size=32),
        'employee_grade': fields.char('Grade'),
        'job_id': fields.many2one('hr.job', 'Designation'),
        'vendor_payment': fields.boolean("Vendor Payment"),
        'vendor_name': fields.char("Vendor Name"),
        'employee_reimb': fields.boolean("Employee Reimbursement"),
        'operational_exp': fields.boolean("Operational Expenses"),
        'capital_expe': fields.boolean("Capital Expenditure"),
        'po_no': fields.char("PO No.", size=5),
        'po_date': fields.date("PO Date:"),
        'po_value': fields.char("PO Value", size=5),
        'planned_ids': fields.one2many('hr.expense.planned', 'expense_id', 'Planned Expense Lines', readonly=True ),
        'daily_ids': fields.one2many('hr.expense.daily', 'expense_id', 'Daily Expense Lines'),
        'line_ids': fields.one2many('hr.expense.line', 'expense_id', 'Expense Lines'),
	'report_summary_id': fields.one2many('hr.expense.summary.report', 'expense_id', 'Report Summary Expense Lines', readonly=True),        
	'amount': fields.function(_amount, string='Total Amount Spent', digits_compute=dp.get_precision('Account')),
        'excess_total_amount': fields.function(_totalExcess_amount, string='Total Excess', digits_compute=dp.get_precision('Account')),
	'budget_amount_total': fields.function(total_budget_amount,string='Total Budget', digits_compute=dp.get_precision('Account')),       
	'planned_amount': fields.function(_planned_amount, string='Total Amount', digits_compute=dp.get_precision('Account')),
        'daily_total_amount': fields.function(_daily_amount, string='Gross Amount', digits_compute=dp.get_precision('Account'), store=True),
        'daily_disallowed_amount': fields.float(string='Disallowed Amount', digits_compute=dp.get_precision('Account'), store=True),
        'advance_amount': fields.function(_advance_paid, string='Advance Paid', digits_compute=dp.get_precision('Account'), store=True),
        'net_amount': fields.function(_net_amount, string='Net Payable Amount', digits_compute=dp.get_precision('Account'), store=True),
        'mode_of_payment': fields.selection([('Cash','Cash'),('Check','Check'),('Online Payment','Online Payment')],'Mode Of Payment'),
#         'expenses': fields.selection([('Employee Reimbursement','Employee Reimbursement'),('Daily Expenses','Daily Expenses'),('Travel Expenses','Travel Expenses')],'Type of Expense'),
        'expenses': fields.selection([('Employee Reimbursement','Employee Reimbursement'),('Travel Expenses','Travel Expenses')],'Type of Expense'),
        'code1': fields.char('Code'),
        'code2': fields.char('Code'),
        'exp_fdate': fields.date('From Date', required=True),
        'exp_tdate': fields.date('To Date', required=True),
        'trip_no':fields.many2one('hr.holidays','Trip No.',read=['base.group_user'], domain = [('business_trip','=',True),('expense_approved','=',False),('state','=','validate')], ),
        'specify_reason_for_refusal_of_expense':fields.boolean('Specify Reason for Refusal of Expense'),
        'reason_for_refusal':fields.text('Reason for Refusal of Expense'),
        'change_in_trip_schedule': fields.boolean('Change In Trip Schedule'),
        'allow_to_claim_expense': fields.boolean('Allow to Claim Expense'),
        'allow_excess_amount': fields.boolean('Allow Excess Amount in Actual Expense'),
        'date_given': fields.date('Payment Given Date', select=True, help="Date when the check was given by the accountant."),
        'user_given': fields.many2one('res.users', 'Payment Given By'),
        'date_received': fields.date('Payment Received Date', select=True, help="Date when the check was received by the employee."),
        'user_received': fields.many2one('res.users', 'Payment Received By'),
        'bank': fields.many2one('res.bank', 'Bank Name'),
        'check_no': fields.char("Check No."),
        'advance_paid': fields.float("Advance Paid"),
        'balance_payment': fields.float("Balance Payment"),
        'amount_paid': fields.float("Amount Paid"),
        'is_advance_paid': fields.boolean('Is Advance Paid'),
        'state': fields.selection([
            ('draft', 'New'),            
            ('Waiting Manager Approval', 'Waiting Manager Approval'),
            ('Approved By Manager', 'Approved By Manager'),
            ('Waiting Accounts Approval', 'Waiting Accounts Approval'),
            ('Approved By Accounts', 'Approved By Accounts'),
            ('Waiting Mgmt Approval', 'Waiting Mgmt Approval'),
            ('Approved By Mgmt', 'Approved By Mgmt'),
            ('done', 'Payment Given'),
            ('paid', 'Payment Received'),
			('cancelled', 'Refused'),
            ],
            'Status', readonly=True),
        
    }
    
    _defaults = {
        'code1': 'EXP',
        'code2': 'ER',
        'state': 'draft',
        'exp_no': lambda obj, cr, uid, context: '/',
        'exp_no1': lambda obj, cr, uid, context: '/',
        #'mode_of_payment': 'Cash',
    }
    
    
    

    
    def compute_expenses(self, cr, uid, ids, context=None):
    	#cr1 = cr
    	
    	print "---------------------------------------------------------"
    	search_expense_lines = self.pool.get('hr.expense.line').search(cr, uid, [('expense_id', '=', ids[0])])
    	print search_expense_lines, "****************************************************************************"
    	total_line_amount = 0.0
    	
    	count=0
    	
    	for l in self.pool.get('hr.expense.line').browse(cr, uid, search_expense_lines):
    		description = l.name
    		unit_amount = l.unit_amount
    		
    		actual_total = l.actual_total
    		
    		total_line_amount = total_line_amount + l.unit_amount
    		
    		previous_record = l.id-1
    		
    		type_of_stay = l.type_of_stay
    		
    		current_date_value = l.date_value
    		
    		emp_grade = l.employee_grade
    		
    		city = l.city
    		
    		no_of_days = l.no_of_days
    		
    		
    		
    	
    		
    		print description, total_line_amount, l.id, previous_record, city.name,"&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
			
		if type_of_stay == 'Boarding':
			
			print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ BOARDING $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
			#cr.execute("update hr_expense_line set actual_total = 0.0 where expense_id=%s and type_of_stay='Boarding'",(ids))
	    		cr.execute("update hr_expense_line set limit_amount = 0.0 where actual_total = 0.0 and expense_id=%s and type_of_stay='Boarding'",(ids))
    			cr.execute("update hr_expense_line set diff_in_amount = 0.0 where actual_total = 0.0 and expense_id=%s and type_of_stay='Boarding'",(ids))		
			if city:            
				city_list = self.pool.get('res.city').search(cr, uid, [('id', '=', city.id)])
				print city_list, "iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
				for m in self.pool.get('res.city').browse(cr, uid, city_list):
					city_name = m.name
					city_classification_level = m.classification_level
				print city_name, city_classification_level, ids, emp_grade, type_of_stay, "gggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg"     

				search_budgetary_amount_boarding = self.pool.get('travel.policies.boarding').search(cr, uid, [('grade', '=', emp_grade),('classification_level', '=', city_classification_level)])

				for v in self.pool.get('travel.policies.boarding').browse(cr, uid, search_budgetary_amount_boarding):
					min_expense_boarding = v.expense_low
					max_expense_boarding = v.expense_high
				print min_expense_boarding, max_expense_boarding, "lllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll"    

				
				cr.execute("select date_value, sum(unit_amount) from hr_expense_line where expense_id = %s and date_value = %s and type_of_stay = 'Boarding' group by date_value",(ids[0],current_date_value))
				list_fetched = cr.fetchall()
				
				print list_fetched, "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ LIST FETCHED @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
				
				list_fetched_dates = list_fetched[0]
				datewise_unit_amount = list_fetched_dates[1]
				print datewise_unit_amount, current_date_value, "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
				count = count+1
				
				print count, "################################# COUNT #####################################"
				
				cr.execute("select date_value, sum(unit_amount), count(*) from hr_expense_line where expense_id = %s and type_of_stay = 'Boarding' group by date_value",(ids))
				count_list_fetched = cr.fetchall()
				print count_list_fetched, current_date_value, "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
				
				
				
				for x in count_list_fetched:
					print x, "ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
					
					list_date = x[0]
					list_total = x[1]
					list_number = x[2]
					
					print count, current_date_value, "444444444444444444444444444444444444444444444444444444444444444444444444"
					print list_date, list_total, list_number, "222222222222222222222222222222222222222222222222222222222222222222222"
				
					#counter = count_list_fetched[0]
					#print counter, "|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||"
					#counter_number = x[1]
					#print counter_number, count, datewise_unit_amount, ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
				
				
					#print count, counter_number,"kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
					#if count == counter_number:
					excess_amount = max_expense_boarding - datewise_unit_amount
					if excess_amount >= 0.0:
						excess_amount = 0.0
			                else:
                                        	excess_amount = -(excess_amount)
					if list_date == current_date_value and count == list_number:
						line_write_id = self.pool.get('hr.expense.line').write(cr, uid, l.id, {'actual_total':datewise_unit_amount, 'limit_amount': max_expense_boarding, 'diff_in_amount':excess_amount}) 
						
						count=0
		
		if type_of_stay == 'Lodging':
			print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ LODGING $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
			actual_total_lodging = l.unit_amount * l.no_of_days
					
			self.pool.get('hr.expense.line').write(cr, uid, l.id, {'actual_total': actual_total_lodging}, context=context)				
		
		
		self.write(cr, uid, ids, {'computed': True}, context=context)				
		#elif type_of_stay == 'Lodging':
		
		#			actual_total_lodging = l.unit_amount * l.no_of_days
					
		#			self.pool.get('hr.expense.line').write(cr, uid, l.id, {'actual_total': actual_total_lodging}, context=context)
									
						#cr.execute('update hr_expense_line set limit_amount = 0.0 where actual_total = 0.0 and expense_id=%s',(ids))
				
					
				
				#cr.execute('update hr_expense_line set actual_total = %s FROM (select date_value, sum(unit_amount) from hr_expense_line where expense_id = %s and date_value = %s group by date_value) as SS where expense_id = %s',(datewise_unit_amount,ids[0],current_date_value,ids[0]))
				
				
				#cr.execute('update hr_expense_line set actual_total = obj.actual_total FROM (select date_value, sum(unit_amount) as actual_total from hr_expense_line where expense_id = %s and date_value = %s group by date_value) as obj, hr_expense_line as exp where obj.actual_total=exp.actual_total and exp.expense_id = %s',(ids[0],current_date_value,ids[0]))
				
				
				#cr.execute('update hr_expense_line set actual_total = sum(unit_amount) where expense_id = %s',(ids))
				#cr.execute('update hr_expense_line set actual_total = (select date_value, sum(unit_amount) from hr_expense_line group by date_value) where expense_id = %s',(ids))
	    # and date_value in (select date_value from hr_expense_line group by date_value)
		#line_write_id = self.pool.get('hr.expense.line').write(cr, uid, l.id, {'actual_total':total_line_amount}) 
			
    def create(self, cr, uid, vals, context=None):
        import time
        from datetime import date
        from datetime import datetime
        if vals.has_key('name') and vals.has_key('exp_fdate') and vals.has_key('exp_tdate') and vals.has_key('employee_id'):
            print vals['employee_id']            
            x = self.pool.get('hr.employee').search(cr,uid,[('id','=', vals['employee_id'])])
            for m in self.pool.get('hr.employee').browse(cr,uid,x):
                name = m.name
            if vals['name'] or vals['exp_fdate'] or vals['exp_tdate'] or vals['employee_id']:
                print vals['exp_tdate'], 'dateettet'
                vals['name'] = str(name) + " - " + str(vals['name']) + " for period from " + str(datetime.strptime(vals['exp_fdate'],"%Y-%m-%d").strftime("%d/%m/%Y")) + " to " + str(datetime.strptime(vals['exp_tdate'],"%Y-%m-%d").strftime("%d/%m/%Y"))
                vals.update({'name':vals['name']})
        res_id = super(hr_expense_expense, self).create(cr, uid, vals, context)
        return res_id
 
    def write(self, cr, uid, ids, vals, context=None):
        import time
        from datetime import date
        from datetime import datetime
        res_id = super(hr_expense_expense, self).write(cr, uid, ids, vals, context=context)
        main_form_id =  ids[0]
        print main_form_id, 'main form id'
        for h in self.browse(cr,uid,ids,context):
            fd = datetime.strptime(h.exp_fdate,"%Y-%m-%d").strftime("%d/%m/%Y")
            td = datetime.strptime(h.exp_tdate,"%Y-%m-%d").strftime("%d/%m/%Y")
            nm = h.name
            nm = nm.split('for')
            print nm, 'namemmm'
            var1 = h.id
        nm1 = nm[0] + " for period from " + str(fd) + " to " + str(td)
        res_id = super(hr_expense_expense, self).write(cr, uid, ids, {'name':nm1}, context=context)
        return res_id

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
        	search_hro = self.pool.get('res.users').search(cr, uid, [('is_hro', '=', True)])
        	
        	if uid in search_hro and rec.employee_id.user_id.id!=uid:
           		raise osv.except_osv(_('Warning!'),_('You cannot delete an expense'))
        	
          	if rec.state != 'draft':
				raise osv.except_osv(_('Warning!'),_('You can only delete draft expenses!'))
        return super(hr_expense_expense, self).unlink(cr, uid, ids, context)
    
    def submit_expenses(self, cr, uid, ids, context=None):
        for h in self.browse(cr, uid, ids, context=None):
            type_of_expense = h.expenses
            planned_details = h.planned_ids
            line_details = h.line_ids
            daily_details = h.daily_ids
            form_id = h.id
            date_of_creation = h.date
            trip_no1 = h.trip_no.trip_no
            fdate = h.exp_fdate
            tdate = h.exp_tdate
            emp_grade = h.employee_grade
            change_in_trip_date = h.change_in_trip_schedule
            allow_to_claim_exp = h.allow_to_claim_expense
            allow_excess_amount = h.allow_excess_amount
            excess_total_amount = h.excess_total_amount
            from_date_year = int( fdate[:4])
            from_date_month = int( fdate[5:7])
            from_date_date = int( fdate[8:10])
            to_date_year = int( tdate[:4])
            to_date_month = int( tdate[5:7])
            to_date_date = int( tdate[8:10])
            date_creation__year = int( date_of_creation[:4])
            date_creation_month = int( date_of_creation[5:7])
            date_creation_date = int( date_of_creation[8:10])
            ex_date_from = date(from_date_year,from_date_month,from_date_date)
            ex_date_to = date(to_date_year,to_date_month,to_date_date)
            ex_date_to_after7 = ex_date_to + relativedelta(days=+7)
            ex_date_of_creation = date(date_creation__year,date_creation_month,date_creation_date)
            computed = h.computed
            if type_of_expense == 'Travel Expenses':
                if not computed:
                    raise osv.except_osv(_('Warning!'),_("Please click on Compute button before submitting your Expenses"))
            today_date = strftime("%Y-%m-%d")
            if str(ex_date_of_creation) < str(today_date):
                raise osv.except_osv(_('Warning!'),_("Date Of Creation Of Expenses can not be less than Today's Date"))
            if type_of_expense == 'Travel Expenses':
                if not allow_to_claim_exp:
                    if str(ex_date_of_creation) > str(ex_date_to_after7):
                        raise osv.except_osv(_('Warning!'),_("Since The Date of Claiming the Expenses has been Exceeded, you are not allowed to claim the Expenses. If you want to claim the Expenses then you need to take Management's approval through mail communication. You are requested to communicate through 'Logging Of Notes' feature. Also you are requested to save this record.\n Note: You are requested to claim the Expenses within 7 days from the date of return."))
            if type_of_expense == 'Employee Reimbursement':
                if not allow_to_claim_exp:
                    if str(ex_date_of_creation) > str(ex_date_to_after7):
                        raise osv.except_osv(_('Warning!'),_("Since The Date of Claiming the Expenses has been Exceeded, you are not allowed to claim the Expenses. If you want to claim the Expenses then you need to take Management's approval through mail communication. You are requested to communicate through 'Logging Of Notes' feature. Also you are requested to save this record.\n Note: You are requested to claim the Expenses within 7 days from the period of Expense."))

        if not planned_details and type_of_expense == 'Travel Expenses':
            raise osv.except_osv(_('Warning!'),_("You need to display and view the planned expenses before you submit the Travel Expenses. Please click on 'Fetch Planned Expenses'"))
        if not line_details and type_of_expense == 'Travel Expenses':
            raise osv.except_osv(_('Warning!'),_("You need to add Actual Expenses before you submit the form."))
        if not daily_details and type_of_expense == 'Employee Reimbursement':
            raise osv.except_osv(_('Warning!'),_("You need to add the Expenses in the Expenses tab before you submit the form."))
        search_trip_record = self.pool.get('hr.holidays').search(cr,uid,[('trip_no','=',trip_no1)], context=context)
        search_actual_expense_line_details = self.pool.get('hr.expense.line').search(cr, uid, [('expense_id', '=', ids[0])])
        search_daily_expense_line_details = self.pool.get('hr.expense.daily').search(cr, uid, [('expense_id', '=', ids[0])])
        search_travel_policies_rules = self.pool.get('travel.policies.rules').search(cr, uid, [('name', '=', 'Travel Policies/Eligibilities')])
        print search_travel_policies_rules
        search_travel_policies_lodging = self.pool.get('travel.policies.lodging').search(cr, uid, [('lodging_id', '=', search_travel_policies_rules[0]),('grade', '=', emp_grade)])
        print search_travel_policies_lodging, "nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn"    
#         is_expense_greater = False
        
        for k in self.pool.get('hr.holidays').browse(cr, uid, search_trip_record):
            planned_id = k.id
            total_approved_amount = -(k.total_approved_amount)
            dt_from = k.date_from
            dt_to = k.date_to
            fdate_year = int( dt_from[:4])
            fdate_month = int( dt_from[5:7])
            fdate_date = int( dt_from[8:10])
            tdate_year = int( dt_to[:4])
            tdate_month = int( dt_to[5:7])
            tdate_date = int( dt_to[8:10])
            tr_date_from = date(fdate_year,fdate_month,fdate_date)
            tr_date_to= date(tdate_year,tdate_month,tdate_date)
            print trip_no1
            
            if not change_in_trip_date:
                if (str(ex_date_from) != str(tr_date_from)) or (str(ex_date_to) != str(tr_date_to)):
                    raise osv.except_osv(_('Warning!'),_("The dates specified for the Expenses of given Business Trip do not match with the original date of the trip.  If the Trip schedule has changed, please click on the checkbox for 'Change in Trip Schedule' and then specify the new dates"))
            if not (str(ex_date_of_creation) >= str(ex_date_to) >= str(ex_date_from)):
                raise osv.except_osv(_('Warning!'),_('The Date of Creation for Expense should be after the Business Trip Duration'))
        
        
        count5=0
        count6=0
        if type_of_expense == 'Travel Expenses':
            t = 1
            count = 0
            count1 = 0
            total = 0.0
            for t in self.pool.get('hr.expense.line').browse(cr, uid, search_actual_expense_line_details):
                planned_expense_date_from = t.date_value
                planned_expense_date_to = t.expense_to
                actual_amount = t.unit_amount
                travel_mode = t.mode_of_travel
                type_of_stay = t.type_of_stay
                city_travel = t.city.name
                attach_file = t.attachment_file
#                invoice_dt = t.invoice_date
#                invoice_no = t.invoice_no
                excess = t.diff_in_amount
                allow_air = t.allow_air_travel
                actual_total = t.actual_total                
#                 total += actual_amount * t.no_of_days
               
                print t, 'Value of tttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt'
#                 print 'ttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt', total, ' totalllllllllllllllllllllllllllll'
                print city_travel, 'citiessssssssssssssssssssssssssss'
                count = count+1
                if not (planned_expense_date_from or planned_expense_date_to):
                    raise osv.except_osv(_('Warning!'),_("In Actual Expenses in the record no. %s, please specify the from and to dates for the corresponding expense")%(count))
                if not (planned_expense_date_from>=fdate and planned_expense_date_to<=tdate):
                    raise osv.except_osv(_('Warning!'),_("In Actual Expenses in the record no. %s, the dates specified do not lie in the range of trip duration")%(count))
                if not city_travel:
                    raise osv.except_osv(_('Warning!'),_("In Actual Expenses in the record no. %s, please select the City")%(count))
                if not type_of_stay:
                    raise osv.except_osv(_('Warning!'),_("In Actual Expenses in the record no. %s, please select the Type")%(count))
                if not actual_amount:
                    raise osv.except_osv(_('Warning!'),_("In Actual Expenses in the record no. %s, please specify the amount for the corresponding expense")%(count))
                if travel_mode == "Air":
                    if not allow_air:
                        raise osv.except_osv(_('Warning!'),_("For the record no. %s, since the Mode of Travel is Air. you need to take Management's approval through mail communication. For that you are first requested to save this record and then communicate through 'Logging Of Notes' feature.")%(count))
                if excess < 0:
                    is_expense_greater = True
#                     raise osv.except_osv(_('Warning!'),_("In Actual Expenses in the record no. %s, Actual Amount is exceeding the budgetary range")%(count))
                #if attach_file:
                    #if not (invoice_dt and invoice_no):
                    #    raise osv.except_osv(_('Warning!'),_("In Actual Expenses in the record no. %s, please specify the Invoice Date and Invoice Number for the added attachment")%(count))
                search_cities = self.pool.get('res.city').search(cr,uid,[('name','=',city_travel)], context=context)
                for p in self.pool.get('res.city').browse(cr, uid, search_cities):
                    classification_level = p.classification_level
                    print classification_level
                    
                
                    search_lodging = self.pool.get('travel.policies.lodging').search(cr,uid,[('grade','=',emp_grade),('classification_level','=',classification_level)], context=context)
                    print search_lodging
                    #grade = m.grade
                    for g in self.pool.get('travel.policies.lodging').browse(cr, uid, search_lodging): 
                        
                        min_expense_lodging = g.expense_low
                        max_expense_lodging = g.expense_high
                        print min_expense_lodging ,"min expense"
                        print max_expense_lodging, "max expense"
                        if type_of_stay == 'Lodging':
                            excess_amt = max_expense_lodging - actual_amount
#                             total += actual_amount * t.no_of_days
#                             print 'ttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt', total, ' totalllllllllllllllllllllllllllll'
                            print max_expense_lodging, 'Maximum Budgetary Expense Value'
                            print excess_amt, 'Excess or within budgetary range Amount For Lodging'
                            #if not invoice_dt:
                            #    raise osv.except_osv(_('Warning'),_("In Actual Expenses in the record no. %s, Enter the Invoice Date for Lodging in the city %s")%(count,city_travel))
                            if not (actual_amount<=max_expense_lodging):
                                excess_amt = max_expense_lodging - actual_amount
                                print excess_amt, 'Excess Amount For Lodging'
                                is_expense_greater = True
#                                 self.write(cr, uid, ids, {'diff_in_amount': excess_amt}, context=context)
#                                 raise osv.except_osv(_('Warning!'),_(excess_amt))
                                
#                                    raise osv.except_osv(_('Warning!'),_("In Actual Expenses in the record no. %s, the amount given %s for lodging in the city %s exceeds the budgetary range %s to %s")%(count,actual_amount,city_travel,min_expense_lodging,max_expense_lodging))
                            
                    
                    
                    
                    search_boarding = self.pool.get('travel.policies.boarding').search(cr,uid,[('grade','=',emp_grade),('classification_level','=',classification_level)], context=context)
                    print search_boarding
                    #grade = m.grade
                    for m in self.pool.get('travel.policies.boarding').browse(cr, uid, search_boarding): 
                        
                        min_expense_boarding = m.expense_low
                        max_expense_boarding = m.expense_high
                        print min_expense_boarding ,"min expense"
                        print max_expense_boarding, "max expense"
                        if type_of_stay == 'Boarding':
                            excess_amt1 = max_expense_boarding - actual_amount
                            print max_expense_boarding, "Maximum Budgetary Expense Value"
                            print excess_amt1, 'Excess or within budgetary range Amount For Boarding'
                            if not (actual_amount<=max_expense_boarding):
                                excess_amt1 = max_expense_boarding - actual_amount
                                print excess_amt1, 'Excess Amount For Boarding'
                                
#                                 raise osv.except_osv(_('Warning!'),_(excess_amt))
#                                 is_expense_greater = True
#                                 raise osv.except_osv(_('Warning!'),_("In Actual Expenses in the record no. %s, the amount given %s for boarding in the city %s exceeds the budgetary range %s to %s")%(count,actual_amount,city_travel,min_expense_boarding,max_expense_boarding))
                total = actual_amount * t.no_of_days
                print 'ttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt', total, ' totalllllllllllllllllllllllllllll'
            create_id = self.write(cr, uid, ids, {'total_amount':total}, context=context)            
            '''if(is_expense_greater):

                return {
                'type': 'ir.actions.act_window',
                'name': _('Expense Approval Request Wizard'),
                'res_model': 'expense.approval.request.wizard',
                'res_id': ids[0],
                'view_type': 'form',
                'view_mode': 'form',
               # 'view_id': form_view_id,
                'target': 'new',
                'nodestroy': True,
                }




            else:
            
                wf_service = netsvc.LocalService('workflow')
                wf_service.trg_validate(uid, 'hr.expense.expense', ids[0], 'order_confirm', cr)

           
                view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hr_expense', 'view_expense_form')
                view_id = view_ref and view_ref[1] or False,
                
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Expense Approval Request Wizard'),
                    'res_model': 'hr.expense.expense',
                    'res_id': ids[0],
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': view_id,
                    'target': 'current',
                    'nodestroy': True,
            }'''
        
        if excess_total_amount < 0:
                if not allow_excess_amount:
                    raise osv.except_osv(_('Warning!'),_("Actual Expenses are over & above Planned/Budgeted Expenses. You need to take Management's approval through mail communication. You are requested to save this record first and then communicate through 'Logging Of Notes' feature."))    
                
        
        if type_of_expense == 'Employee Reimbursement':
        
            for t in self.pool.get('hr.expense.daily').browse(cr, uid, search_daily_expense_line_details):
                daily_expense_date_from = t.date_value
                daily_expense_date_to = t.expense_to
                
                count6 = count6+1
                
                if not (daily_expense_date_from>=fdate and daily_expense_date_from<=tdate):
                    raise osv.except_osv(_('Warning!'),_("In Expenses in the record no. %s, the date specified do not lie in the range of period of expense")%(count6))
        
        
        
        
        '''def _amount_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        total = 0.0
        i = 1
        j = i-1
        
        #search_expense_records = self.search(cr, uid, [('user_id', '=', uid)], context=context)
        
        for i in self.browse(cr, uid, ids, context=context):
#             if expense.type_of_stay == 'Daily Allowances':
#             for j in self.browse(cr, uid, ids, context=context):
            total += i.unit_amount * i.no_of_days
            #print total
            print i.limit, i.city.name, i.date_value, i.expense_to, "iiiiiiiiiiiii I VALUE iiiiiiiiiiiiiiiiiiiiiiiiii"
#             print j.limit, j.city.name,j.date_value, j.expense_to,"jjjjjjjjjjjjj J VALUE jjjjjjjjjjjjjjjjjjjjjjjjjj"
            res[i.id] = total
        return res'''
        
        
        
        for e in self.browse(cr, uid, ids, context=None):
            type_of_expense = e.expenses
            if type_of_expense == 'Employee Reimbursement':
                code_exp = e.code2
            else:
                code_exp = e.code1
            print code_exp,'In the Generation of Auto Sequence no'
            if type_of_expense == 'Travel Expenses':
                print "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
                
                search_sequence_record1 = self.pool.get('ir.sequence').search(cr,uid,[('code','=','hr.expense.expense')], context=context)
                
                print search_sequence_record1, "ttttttttttttttttttttttttttttttttttttttttttt"
                
                self.pool.get('ir.sequence').write(cr, uid, search_sequence_record1, {'prefix': code_exp})
                
                exp_no1 = self.pool.get('ir.sequence').get(cr, uid, 'hr.expense.expense') or '/'
                
                print exp_no1, type(exp_no1), "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
                
                sequence_number_of_trip = exp_no1
                print sequence_number_of_trip
                self.write(cr, uid, ids, {'exp_no':sequence_number_of_trip}) 
            if type_of_expense == 'Employee Reimbursement':
                print "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
                
                search_sequence_record = self.pool.get('ir.sequence').search(cr,uid,[('code','=','hr.employee.confirmation')], context=context)
                
                print search_sequence_record, "ttttttttttttttttttttttttttttttttttttttttttt"
                
                self.pool.get('ir.sequence').write(cr, uid, search_sequence_record, {'prefix': code_exp})
                
                exp_no = self.pool.get('ir.sequence').get(cr, uid, 'hr.employee.confirmation') or '/'
                
                print exp_no, type(exp_no), "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
                
                sequence_number_of_trip = exp_no
                print sequence_number_of_trip
                self.write(cr, uid, ids, {'exp_no1':sequence_number_of_trip}) 
        
        expense_approver_india = ['aradhana','sweta','keshav','nitin']
        for record in self.browse(cr, uid, ids, context=context):
            subscribe_ids = []
            subscribe_ids2 = []
            subscribe_ids3 = []
            
            if record.employee_id and record.employee_id.parent_id and record.employee_id.parent_id.user_id:
                subscribe_ids = [record.employee_id.parent_id.user_id.id,record.employee_id.hro.id]
            
                
            #TODO get company, its HR users and add
            
            if record.employee_id.company_id.id == 1: #Zeeva INDIA
                subscribe_ids += self.pool.get('res.users').search(cr, SUPERUSER_ID, [('login','in',expense_approver_india)])
            
            
                
            subscribe_ids.append( record.employee_id.user_id.id) #related employee added to the follower list
            
            self.message_subscribe_users(cr, SUPERUSER_ID, [record.id], user_ids=subscribe_ids, context=context)
	search_expense_daily = self.pool.get('hr.expense.daily').search(cr, uid, [('expense_id', '=', ids[0])])
        search_summary = self.pool.get('mail.message').search(cr, uid, [('model', '=', 'hr.expense.expense'),('res_id', '=', ids[0])])
        print search_summary
        for l in self.pool.get('mail.message').browse(cr, uid, search_summary):
            author = l.author_id.name
            date_meesage = l.date
            body = html2text(l.body)
            #print author, date_meesage, body, 'Messsssssssssssssssagggggggggg Historyyyyyyyyyyyyyy'
        cr.execute('delete from hr_expense_summary_report where expense_id=%s',([form_id]))
        print search_expense_daily, 'fasdfdaffsssssssssssssss' 
        total_line_amount = 0.0
        budget = 0.0
        count=0
        serial_no=0
        expense_heads=[]
        amount_list=[]
        values = {}
        for l in self.pool.get('hr.expense.daily').browse(cr, uid, search_expense_daily):
            expense_type = l.product_id.name
            unit_amount = l.unit_amount
            
            if not values.has_key(expense_type): 
                values[expense_type] = [unit_amount]
            else:
                values[expense_type].append(unit_amount)  
            expense_heads.append(expense_type)
            amount_list.append(unit_amount)
        
        
        values = {k:sum(v) for k,v in values.items()}  
        print values, 'dictionaryyyyyyyyyyyyyyyyy 1' 
        sr_no = 0
        for key, value in values.iteritems() :
            print key, value
            sr_no  = sr_no + 1
            create_id1 = self.pool.get('hr.expense.summary.report').create(cr, uid, {'serial_no':sr_no,'product_name':str(key), 'total_amount':str(value),  'expense_id':form_id}, context=context)            
	if type_of_expense == 'Employee Reimbursement':
	    return self.write(cr, uid, ids, {'state': 'Waiting Manager Approval','date_valid': time.strftime('%Y-%m-%d'), 'user_valid': uid}, context=context)
        else:
            return self.write(cr, uid, ids, {'state': 'Waiting Manager Approval','total_approved_amount': total_approved_amount, 'date_valid': time.strftime('%Y-%m-%d'), 'user_valid': uid}, context=context)
    
    def expense_confirm(self, cr, uid, ids, context=None):
        for expense in self.browse(cr, uid, ids):
            if expense.employee_id and expense.employee_id.parent_id.user_id:
                self.message_subscribe_users(cr, uid, [expense.id], user_ids=[expense.employee_id.parent_id.user_id.id])
        return self.write(cr, uid, ids, {'state': 'Waiting Accounts Approval', 'date_confirm': time.strftime('%Y-%m-%d')}, context=context)   
    
    def validate_manager(self, cr, uid, ids, context=None):
	for x in self.browse(cr, uid, ids, context=None):
	    employee_id = x.employee_id.id
	#if x.employee_id.user_id.id == uid:
    #        raise osv.except_osv(_('Warning!'),_('You cannot Approve your own Expenses'))
	return self.write(cr, uid, ids, {'state': 'Approved By Manager', 'date_valid': time.strftime('%Y-%m-%d'), 'user_valid': uid}, context=context)
    
    def submit_to_accounts(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'Waiting Accounts Approval', 'date_valid': time.strftime('%Y-%m-%d'), 'user_valid': uid}, context=context)
    
    def validate_accounts(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'Approved By Accounts', 'date_valid': time.strftime('%Y-%m-%d'), 'user_valid': uid}, context=context)
    
    
    def draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)
    
    def expense_canceled(self, cr, uid, ids, context=None):
        for x in self.browse(cr, uid, ids, context=None):
            specify_reason_for_refusal = x.specify_reason_for_refusal_of_expense
            reason_for_refusal = x.reason_for_refusal
            employee_id = x.employee_id.id
        if x.employee_id.user_id.id == uid:
            raise osv.except_osv(_('Warning!'),_('You cannot Refuse your own Expenses'))
        if specify_reason_for_refusal == False:
            raise osv.except_osv(_('Warning!'),_("Please specify a reason for refusal. Click on the checkbox for 'Specify reason for refusal of Expense'"))
        elif not reason_for_refusal:
            raise osv.except_osv(_('Warning!'),_("Please specify a reason for refusal of Expense"))
        else:
            return self.write(cr, uid, ids, {'state': 'cancelled'}, context=context)
        
    def expense_canceled_accounts(self, cr, uid, ids, context=None):
        for x in self.browse(cr, uid, ids, context=None):
            specify_reason_for_refusal = x.specify_reason_for_refusal_of_expense
            reason_for_refusal = x.reason_for_refusal
        if specify_reason_for_refusal == False:
            raise osv.except_osv(_('Warning!'),_("Please specify a reason for refusal. Click on the checkbox for 'Specify reason for refusal of Expense'"))
        elif not reason_for_refusal:
            raise osv.except_osv(_('Warning!'),_("Please specify a reason for refusal of Expense"))
        else:
            return self.write(cr, uid, ids, {'state': 'cancelled'}, context=context)
    
    
    def validate_mgmt(self, cr, uid, ids, context=None):
        for x in self.browse(cr, uid, ids, context=None):
            trip_no1 = x.trip_no.trip_no
            type_of_expense = x.expenses
            search_trip_record = self.pool.get('hr.holidays').search(cr,uid,[('trip_no','=',trip_no1)], context=context)
            for k in self.pool.get('hr.holidays').browse(cr, uid, search_trip_record):
                planned_id = k.id
#             message = _("<b>Expense for the %s has been approved. Please, proceed with the Payments</b>") % (x.trip_no.name)
#             self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)
            if type_of_expense == 'Travel Expenses':
                self.pool.get('hr.holidays').write(cr, uid, search_trip_record, {'expense_approved': True }, context=context)
        return self.write(cr, uid, ids, {'state': 'Approved By Mgmt', 'date_valid': time.strftime('%Y-%m-%d'), 'user_valid': uid}, context=context)
    
    def confirm_mgmt(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'Waiting Mgmt Approval', 'date_valid': time.strftime('%Y-%m-%d'), 'user_valid': uid}, context=context)
        
    def action_payment_given(self, cr, uid, ids, context=None):
        for x in self.browse(cr, uid, ids, context=None):
            amount_paid = x.amount_paid
            type_of_expense = x.expenses
            amount = x.payable_amount
            print amount, 'In the Travel Expense'
            net_amount = x.net_amount
	    daily_total_amount = x.daily_total_amount
            advance_paid = x.advance_paid
            print net_amount, 'In the emp reimbursement expense'
        if type_of_expense == 'Travel Expenses':
			
            if not amount_paid:
                raise osv.except_osv(_('Warning!'),_("Please enter the Amount Paid for this Business Trip in the Payment Status Tab"))
            if amount_paid > amount:
                raise osv.except_osv(_('Warning!'),_("Please enter the valid Amount Paid for this Business Trip in the Payment Status Tab"))
        if type_of_expense == 'Employee Reimbursement':
	    if daily_total_amount != advance_paid:
		if not amount_paid:
		    raise osv.except_osv(_('Warning!'),_("Please enter the Amount Paid for this expense in the Payment Status Tab"))
            if amount_paid > net_amount:
                raise osv.except_osv(_('Warning!'),_("Please enter the valid Amount Paid for this expense in the Payment Status Tab"))
        if type_of_expense == 'Travel Expenses':
            message = _("Payment of %s Expenses has been given") % (x.trip_no.name)
        else:
            message = _("Payment of %s has been given") % (x.name)
        self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)
        return self.write(cr, uid, ids, {'state': 'done','date_given': time.strftime('%Y-%m-%d'), 'user_given': uid}, context=context)
            
    def action_payment_received(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'paid','date_received': time.strftime('%Y-%m-%d'), 'user_received': uid}, context=context)
    
    
    
    def display_expenses(self, cr, uid, ids, context=None):
        for x in self.browse(cr, uid, ids, context=None):
            form_id = x.id
            trip_no1 = x.trip_no.trip_no
            fdate = x.exp_fdate
            tdate = x.exp_tdate
            change_in_trip_date = x.change_in_trip_schedule
            from_date_year = int( fdate[:4])
            from_date_month = int( fdate[5:7])
            from_date_date = int( fdate[8:10])
            to_date_year = int( tdate[:4])
            to_date_month = int( tdate[5:7])
            to_date_date = int( tdate[8:10])
            ex_date_from = date(from_date_year,from_date_month,from_date_date)
            ex_date_to= date(to_date_year,to_date_month,to_date_date)
            print trip_no1
            search_trip_record = self.pool.get('hr.holidays').search(cr,uid,[('trip_no','=',trip_no1)], context=context)
            for k in self.pool.get('hr.holidays').browse(cr, uid, search_trip_record):
                planned_id = k.id
                dt_from = k.date_from
                dt_to = k.date_to
                fdate_year = int( dt_from[:4])
                fdate_month = int( dt_from[5:7])
                fdate_date = int( dt_from[8:10])
                tdate_year = int( dt_to[:4])
                tdate_month = int( dt_to[5:7])
                tdate_date = int( dt_to[8:10])
                tr_date_from = date(fdate_year,fdate_month,fdate_date)
                tr_date_to= date(tdate_year,tdate_month,tdate_date)
                print trip_no1
                if not change_in_trip_date:
                    if (str(ex_date_from) != str(tr_date_from)) or (str(ex_date_to) != str(tr_date_to)):
                        raise osv.except_osv(_('Warning!'),_('The dates specified for the Expenses of given Business Trip do not match with the original date of the trip.'))
                cr.execute('delete from hr_expense_planned where expense_id=%s',([form_id]))
                search_planned_details = self.pool.get('planned.budget.expenses').search(cr, uid, [('planned_budget_id', '=', planned_id)])
                    
            for m in self.pool.get('planned.budget.expenses').browse(cr, uid, search_planned_details):
                sr_no = m.sr_no
                source = m.source
                destination = m.destination
                name = m.description
                fdate = m.expense_from
                tdate = m.expense_to
                no_of_days = m.no_of_days
                mode_of_travel = m.mode_of_travel
                city = m.city.id
                type_of_stay = m.type_of_stay
                unit_amount = m.unit_amount
                total_amount = m.total_amount
            
                create_id = self.pool.get('hr.expense.planned').create(cr, uid, {'sequence':sr_no,'source':source, 'destination':destination, 'date_value':fdate, 'expense_to': tdate, 'name': name, 'no_of_days': no_of_days, 'mode_of_travel': mode_of_travel, 'city': city, 'unit_amount': unit_amount, 'total_amount': total_amount, 'type_of_stay':type_of_stay,'expense_id':form_id}, context=context)
        return create_id
                
        
      
    
    def onchange_trip_no(self, cr, uid, ids, trip_no):
        """
        Update the number_of_days.
        """

        # date_to has to be greater than date_from
        value = {'date_from': False, 'date_to': False}
        if trip_no:
            emp = self.pool.get('hr.holidays').browse(cr, uid, trip_no)
            value['date_from'] = emp.date_from[:10]
            value['date_to'] = emp.date_to[:10]
            from_date_year = int( emp.date_from[:4])
            from_date_month = int( emp.date_from[5:7])
            from_date_date = int( emp.date_from[8:10])
            to_date_year = int( emp.date_to[:4])
            to_date_month = int( emp.date_to[5:7])
            to_date_date = int( emp.date_to[8:10])
            date_from = date(from_date_year,from_date_month,from_date_date)
            date_to= date(to_date_year,to_date_month,to_date_date)
            value['exp_fdate'] = str(date_from)
            value['exp_tdate'] = str(date_to)
        return {'value': value}

    
        
    def onchange_exp_tdate(self, cr, uid, ids, exp_fdate, exp_tdate, date, expenses):
        """
        Update the number_of_days.
        """
       
        from dateutil.relativedelta import relativedelta
        import datetime
        from datetime import date as date_exp
        from datetime import timedelta
        from time import strftime
        print exp_tdate
        print date, "sadaddddddddddddddddddddddddddddddddddddddddddddddd"
        date_year = int(exp_tdate[:4])
        date_month = int(exp_tdate[5:7])
        date_date = int(exp_tdate[8:10])
        print date_date, date_month, date_year, "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD"
        date_after_7days = date_exp(date_year,date_month,date_date) + relativedelta(days=+7)
        date_creation_year = int(date[:4])
        date_creation_month = int(date[5:7])
        date_creation_date = int(date[8:10])
        date_creation = date_exp(date_creation_year,date_creation_month,date_creation_date)
        newobj = str(date_after_7days)
        print newobj
        # date_to has to be greater than date_from
        if expenses == 'Travel Expenses':
            if date_creation > date_after_7days:
                raise osv.except_osv(_('Warning!'),_("Since The Date of Claiming the Expenses has been Exceeded, you are not allowed to claim the Expenses. If you want to claim the Expenses then you need to take Management's approval through mail communication. You are requested to communicate through 'Logging Of Notes' feature. Also you are requested to save this record.\n Note: You are requested to claim the Expenses within 7 days from the date of return."))
        if expenses == 'Employee Reimbursement':
            if date_creation > date_after_7days:
                raise osv.except_osv(_('Warning!'),_("Since The Date of Claiming the Expenses has been Exceeded, you are not allowed to claim the Expenses. If you want to claim the Expenses then you need to take Management's approval through mail communication. You are requested to communicate through 'Logging Of Notes' feature. Also you are requested to save this record.\n Note: You are requested to claim the Expenses within 7 days from the period of Expense."))
        if date < exp_fdate:
            raise osv.except_osv(_('Warning!'),_('The date of creation cannot be less than period of expense.'))         
        if (exp_fdate and exp_tdate) and (exp_fdate > exp_tdate):
            raise osv.except_osv(_('Warning!'),_('The From date must be anterior of the To date.'))
        
        return False
    
     
    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        emp_obj = self.pool.get('hr.employee')
        department_id = False
        company_id = False
        job_id = False
        employee_grade = False
        if employee_id:
            employee = emp_obj.browse(cr, uid, employee_id, context=context)
            department_id = employee.department_id.id
            company_id = employee.company_id.id
            job_id = employee.job_id.id
            employee_grade = employee.employee_grade
        return {'value': {'department_id': department_id, 'job_id': job_id, 'employee_grade': employee_grade}}
    
    def onchange_advance_paid(self, cr, uid, ids, advance_paid, daily_total_amount ,context=None):
        
        if advance_paid:
            balance_payment = daily_total_amount - advance_paid 
        return {'value': {'balance_payment': balance_payment}}
    
    
    def onchange_vendor_payment(self, cr, uid, ids, vendor_payment, context=None):
        return {'value': {'vendor_payment':vendor_payment,'employee_reimb': False,'operational_exp':False,'capital_expe': False}}
    
    def onchange_employee_reimb(self, cr, uid, ids, employee_reimb, context=None):
        return {'value': {'vendor_payment':False,'employee_reimb': employee_reimb,'operational_exp':False,'capital_expe': False}}
    
    def onchange_operational_exp(self, cr, uid, ids, operational_exp, context=None):
        return {'value': {'vendor_payment':False,'employee_reimb': False,'operational_exp':operational_exp,'capital_expe': False}}
    
    def onchange_capital_expe(self, cr, uid, ids, capital_expe, context=None):
        return {'value': {'vendor_payment':False,'employee_reimb': False,'operational_exp':False,'capital_expe': capital_expe}}
	
    def act_employee_business_trip(self, cr, uid, ids, context=None):
        for x in self.browse(cr, uid, ids, context=None):
            form_id = x.id
            trip_no1 = x.trip_no.trip_no
            search_trip_record = self.pool.get('hr.holidays').search(cr,uid,[('trip_no','=',trip_no1)], context=context)
            for k in self.pool.get('hr.holidays').browse(cr, uid, search_trip_record):
                planned_id = k.id
        if context is None: context = {}
        if not ids: return False
        if not isinstance(ids, list): ids = [ids]
        ir_model_data = self.pool.get('ir.model.data')        
        view_ref = ir_model_data.get_object_reference(cr, uid, 'zeeva_hr', 'edit_business_trips_new')
        view_id = view_ref and view_ref[1] or False,
        return {
           'type': 'ir.actions.act_window',
           'name': 'Business Trip',
           'view_mode': 'form',
           'view_type': 'form',
           'view_id': view_id,
           'res_model': 'hr.holidays',
           'res_id': planned_id,
           'domain': [('business_trip','=',True)],
        }        



class hr_expense_line(osv.osv):
    _name = "hr.expense.line"
    _inherit = 'hr.expense.line'
    _order = 'date_value'
    
    
    '''def _amount_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        total = 0.0
        i = 1
        j = i-1
        
        #search_expense_records = self.search(cr, uid, [('user_id', '=', uid)], context=context)
        
        for i in self.browse(cr, uid, ids, context=context):
#             if expense.type_of_stay == 'Daily Allowances':
#             for j in self.browse(cr, uid, ids, context=context):
            total += i.unit_amount * i.no_of_days
            #print total
            print i.limit, i.city.name, i.date_value, i.expense_to, "iiiiiiiiiiiii I VALUE iiiiiiiiiiiiiiiiiiiiiiiiii"
#             print j.limit, j.city.name,j.date_value, j.expense_to,"jjjjjjjjjjjjj J VALUE jjjjjjjjjjjjjjjjjjjjjjjjjj"
            res[i.id] = total
        return res'''
    
    def _amount(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}
        res = {}    
        print ids, "hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh"
        for j in self.browse(cr, uid, ids, context=context):
        	res1 = 0.0
        	res2 = 0.0
        	type_of_stay = j.type_of_stay
        	
        	if type_of_stay == 'Travelling':
        		print "mmmmmmmmmmmmmmmmmmmmmmmmmmmmm TRAVELLING mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm"
        		
        		res1 = j.unit_amount
        		print res1, "-------------------------------------------------------------------------"
        		res[j.id] = res1
        		
        	
        	elif type_of_stay in ['Lodging','Boarding']:
        		print "pppppppppppppppppppppppppppppppppp LODGING pppppppppppppppppppppppppppppppppp"	
        		
        		res2 = j.unit_amount * j.no_of_days
        		print res2, "---------------------------------------------------------------------------"
        		res[j.id] = res2
        		
        return res
    
    def _excess_amount(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}
        cr.execute("SELECT l.id,COALESCE(SUM(l.diff_in_amount*l.no_of_days),0) AS amount FROM hr_expense_line l WHERE id IN %s GROUP BY l.id ",(tuple(ids),))
        res = dict(cr.fetchall())
        return res
    
    def _total_budget(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}
        cr.execute("SELECT l.id,COALESCE(SUM(l.limit_amount*l.no_of_days),0) AS amount FROM hr_expense_line l WHERE id IN %s GROUP BY l.id ",(tuple(ids),))
        res = dict(cr.fetchall())
        return res 
    
    def copy(self, cr, uid, id, default=None, context=None):
#         for x in self.browse(cr,uid,id,default=None, context=None):
#             department_id = x.department_id
#         print department_id, "oooooooooooooooooooooooooooooooooooo"
        if not default:
            default = {}
        default.update({
            'sequence': self.pool.get('ir.sequence').get(cr, uid, 'hr.employee'),
            #'auto_emp_code_same': self.pool.get('ir.sequence').get(cr, uid, 'hr.employee'),
        })
        return super(hr_expense_line, self).copy(cr, uid, id, default, context=context)
    
    def _employee_get(self, cr, uid, context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            return ids[0]
        return False
        
    def _get_employee_grade(self, cr, uid, context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        employee = self.pool.get('hr.employee').browse(cr, uid, ids[0])
        if ids:
            return employee.employee_grade
        return False
    
    _columns = {
        'date_value': fields.date('Date'),
        'employee_id': fields.many2one('hr.employee', 'Employee'), 
        'employee_grade':fields.selection([('A1', 'A1'),('B1', 'B1'),('B2', 'B2'),('C1', 'C1'),('C2', 'C2'),('C3', 'C3')], 'Grade'),
        'expense_to': fields.date('Expense To Date'),
#        'invoice_date': fields.date('Invoice Date'),
#        'invoice_no': fields.char('Invoice No.'),
        'uom_id': fields.many2one('product.uom', 'Unit of Measure'),         
        'attachment_file':fields.binary('Attachment'),
        'allow_air_travel': fields.boolean("Allow Air Travel"),
        'city': fields.many2one('res.city', 'City'),
        'source': fields.char('Source'),
        'diff_in_amount': fields.float('Excess'),
        'limit_amount': fields.float('Budget Limit'),
        'destination': fields.char('Destination'),
        'no_of_days': fields.integer('No Of Days'),
#         'actual_total': fields.function(_amount_total, string='Actual Total', digits_compute=dp.get_precision('Account')),
        'actual_total': fields.float(string='Actual Total', digits_compute=dp.get_precision('Account')),
        'total_amount': fields.function(_amount, type='float', string='Total Amount'),
#        'total_amount': fields.float(string='Total Amount', digits_compute=dp.get_precision('Account')),
        'total_budget': fields.function(_total_budget, string='Total Budget', digits_compute=dp.get_precision('Account'),store=True),
        'total_excess_amount': fields.function(_excess_amount, string='Total Excess', digits_compute=dp.get_precision('Account')), 
        'unit_amount': fields.float('Unit Price', digits_compute=dp.get_precision('Product Price')),
        'type_of_stay': fields.selection([('Travelling','Travelling'),('Lodging','Lodging (Hotel Accomodation)'),('Boarding','Daily Allowances')], "Type"),        
        'mode_of_travel': fields.selection([('Air','Air'),('Auto','Auto'),('Bus','Bus'),('Car','Car'),('Train','Train'),('Private Vehicle','Private Vehicle'),('Taxi','Taxi')], "Mode Of Travel"),        
    }
    
    _defaults = {
        'date_value':'',
        'employee_id': _employee_get,
        'employee_grade': _get_employee_grade,
    }
    
    
    def _get_number_of_days(self, date_value, expense_to):
        """Returns a float equals to the timedelta between two dates given as string."""


        date_from_year = int(date_value[:4])
        date_from_month = int(date_value[5:7])
        date_from_date = int(date_value[8:10])

        date_to_year = int(expense_to[:4])
        date_to_month = int(expense_to[5:7])
        date_to_date = int(expense_to[8:10])
        


        d1 = date(date_from_year,date_from_month,date_from_date)
        d2 = date(date_to_year,date_to_month,date_to_date)

        print d1,d2, "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"

        delta = d2 - d1
        
        diff_day = delta.days
        
        print diff_day, "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1"

        return diff_day
    
    
    def onchange_expense_from(self, cr, uid, ids, expense_to, date_value, type_of_stay):
        """
        If there are no date set for date_to, automatically set one 8 hours later than
        the date_from.
        Also update the number_of_days.
        """
        # date_to has to be greater than date_from

        if (date_value and expense_to) and (date_value > expense_to):
            raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

        result = {'value': {}}
        
        if (expense_to and date_value) and (date_value <= expense_to):
            diff_day = self._get_number_of_days(date_value, expense_to)
            if type_of_stay == 'Lodging':
                print diff_day, round(math.floor(diff_day))+1, "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
                result['value']['no_of_days'] = int(round(math.floor(diff_day)))
            elif type_of_stay in ('Boarding', 'Travelling'):
                result['value']['no_of_days'] = int(round(math.floor(diff_day))+1)
            else:
                result['value']['no_of_days'] = int(round(math.floor(diff_day))+1)
            return result
        else:
            result['value']['no_of_days'] = 0

            return result
            
        
    def onchange_expense_to(self, cr, uid, ids, expense_to, date_value, type_of_stay):
        """
        Update the number_of_days.
        """

        # date_to has to be greater than date_from

        if (date_value and expense_to) and (date_value > expense_to):
            raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

        result = {'value': {}}
        
        if (expense_to and date_value) and (date_value <= expense_to):
            diff_day = self._get_number_of_days(date_value, expense_to)
            if type_of_stay == 'Lodging':
                print diff_day, round(math.floor(diff_day))+1, "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
                result['value']['no_of_days'] = int(round(math.floor(diff_day)))
            elif type_of_stay in ('Boarding', 'Travelling'):
                result['value']['no_of_days'] = int(round(math.floor(diff_day))+1)
            else:
                result['value']['no_of_days'] = int(round(math.floor(diff_day))+1)
            return result
            
        else:
            result['value']['no_of_days'] = 0

            return result
            
        
    
   
    def onchange_city(self, cr, uid, ids, employee_grade, type_of_stay, city, limit_amount, unit_amount, date_value, expense_to):
        if employee_grade and type_of_stay:
            print city, "ttttttttttttttttttttttttttttttttttttttttttttttttttttt" 
            
            if type_of_stay == 'Travelling':
                    values = {}
                    
                    if date_value and expense_to:
                        print "mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm"
                        if (date_value and expense_to) and (date_value > expense_to):
                            raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))
        
                        
                
                        if (expense_to and date_value) and (date_value <= expense_to):
                            diff_day = self._get_number_of_days(date_value, expense_to)
                            
                            no_of_days = int(round(math.floor(diff_day))+1)
                           
                
                        values.update({'no_of_days': no_of_days})
                                
                    else:
                        
                        values.update({'no_of_days': 0})
                    
                    if city and unit_amount and date_value and expense_to:
                        diff = limit_amount - unit_amount
                        values = {'limit_amount': unit_amount,'diff_in_amount': diff, 'no_of_days': no_of_days}
                        
               
                       
            if type_of_stay == 'Lodging':
                    values = {}
                    if city:
                    
                        city_id = self.pool.get('res.city').search(cr, uid, [('id', '=', city)])
                        for m in self.pool.get('res.city').browse(cr, uid, city_id):
                            city_name = m.name
                            city_classification_level = m.classification_level
                        print city_name, city_classification_level, ids, employee_grade, type_of_stay, "gggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg"     
                        
                        search_budgetary_amount = self.pool.get('travel.policies.lodging').search(cr, uid, [('grade', '=', employee_grade),('classification_level', '=', city_classification_level)])
                        if city_name == "Mumbai":
                            raise osv.except_osv(_('Warning!'),_('Lodging is not allowed in the Mumbai City'))
                        for u in self.pool.get('travel.policies.lodging').browse(cr, uid, search_budgetary_amount):
                            min_expense = u.expense_low
                            max_expense = u.expense_high
                        print min_expense, max_expense, "lllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll"    
                
                        values = {
                            'limit_amount': max_expense,
                    
                                }
                        if city and limit_amount and unit_amount:
                            diff = limit_amount - unit_amount
                            if diff >= 0.0:
                                values.update({'diff_in_amount': 0.0})
                            else:
                                values.update({'diff_in_amount': -(diff)})
                    else:
                                         
                        values = {
                        'limit_amount': False,
                
                            }
                        
                    if date_value and expense_to:
                        print "mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm"
                        if (date_value and expense_to) and (date_value > expense_to):
                            raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))
        
                        
                
                        if (expense_to and date_value) and (date_value <= expense_to):
                            diff_day = self._get_number_of_days(date_value, expense_to)
                            
                            no_of_days = int(round(math.floor(diff_day)))
                            
                        
                
                            
                
                        values = {
                            'no_of_days': no_of_days
                    
                                }
                                
                                
                    
                        
                    if city and date_value and expense_to:
                        diff = limit_amount - unit_amount
			if diff >= 0.0:
                            diff = 0.0
                        else:
                            diff = -(diff)                        
			print "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"            
                        values = {
                            'diff_in_amount': diff,
                            'limit_amount': max_expense,
                            'no_of_days': no_of_days
                    
                                }  
                        
                    if city and date_value and expense_to and limit_amount:
                        diff = limit_amount - unit_amount
			if diff >= 0.0:
                            diff = 0.0
                        else:
                            diff = -(diff)
                        print "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"            
                        values = {
                            'diff_in_amount': diff,
                            'limit_amount': max_expense,
                            'no_of_days': no_of_days
                    
                                }
                    
                        
            if type_of_stay == 'Boarding':
                    values = {}
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
                            'limit_amount': max_expense_boarding,
                    
                            }
                        if city and limit_amount:
                            diff = limit_amount - unit_amount
                            if diff >= 0.0:
                                values.update({'diff_in_amount': 0.0})
                            else:
                                values.update({'diff_in_amount': -(diff)})
                    
                
                    else:
                        
                        values = {
                            'limit_amount': False,
                
                                }
                        
                    if date_value and expense_to:
                        print "mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm"
                        if (date_value and expense_to) and (date_value > expense_to):
                            raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))
        
                        
                
                        if (expense_to and date_value) and (date_value <= expense_to):
                            diff_day = self._get_number_of_days(date_value, expense_to)
                            
                            no_of_days = int(round(math.floor(diff_day))+1)
                            
                        
                
                            
                
                        values = {
                            'no_of_days': no_of_days
                    
                                }
                                
                        
                    if city and date_value and expense_to:
                        diff = limit_amount - unit_amount
			if diff >= 0.0:
                            diff = 0.0
                        else:
                            diff = -(diff)
                        print "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"            
                        values = {
                            'diff_in_amount': diff,
                            'limit_amount': max_expense_boarding,
                            'no_of_days': no_of_days
                    
                                }
                        
                    if city and limit_amount and unit_amount:
                        diff = limit_amount - unit_amount
			if diff >= 0.0:
                            diff = 0.0
                        else:
                            diff = -(diff)
                        print "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"            
                        values = {
                            'diff_in_amount': diff,
                            'limit_amount': max_expense_boarding,
                            'no_of_days': no_of_days
                    
                                }
                            
            return {'value' : values}
        

    '''def onchange_limit(self, cr, uid, ids, type_of_stay, limit, unit_amount):
        if limit and unit_amount:     
            diff = limit - unit_amount
            print diff ,'difffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
            values = {
                'diff_in_amount': diff
                    }
            
            return {'value' : values}'''    
               
        
   
class hr_expense_planned(osv.osv):
    _name = "hr.expense.planned"   
    
    def _amount(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}
        cr.execute("SELECT l.id,COALESCE(SUM(l.unit_amount*l.no_of_days),0) AS amount FROM hr_expense_planned l WHERE id IN %s GROUP BY l.id ",(tuple(ids),))
        res = dict(cr.fetchall())
        return res

    def _get_uom_id(self, cr, uid, context=None):
        result = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'product', 'product_uom_unit')
        return result and result[1] or False
    
    _columns = {
        'analytic_account': fields.many2one('account.analytic.account','Analytic account'),
        'date_value': fields.date('Expense From Date', required=True),
        'name': fields.char('Description Of Expense', size=128, required=True),
        'expense_id': fields.many2one('hr.expense.expense', 'Expense', ondelete='cascade', select=True),
        'expense_to': fields.date('Expense To Date'),
        'invoice_date': fields.date('Invoice Date'),
        'invoice_no': fields.char('Invoice No.'),
        'uom_id': fields.many2one('product.uom', 'Unit of Measure'),         
        #'attachment_file':fields.binary('Attachment'),
        'source': fields.char('Source'),
        'destination': fields.char('Destination'),
        'type_of_stay': fields.selection([('Travelling','Travelling'),('Lodging','Lodging (Hotel Accomodation)'),('Boarding','Boarding (Daily Allowance)')], "Type"),        
        'mode_of_travel': fields.selection([('Air','Air'),('Auto','Auto'),('Bus','Bus'),('Car','Car'),('Train','Train'),('Private Vehicle','Private Vehicle'),('Taxi','Taxi')], "Mode Of Travel"),        
        'total_amount': fields.function(_amount, string='Total', digits_compute=dp.get_precision('Account')),
        'unit_amount': fields.float('Unit Price', digits_compute=dp.get_precision('Product Price')),
        'unit_quantity': fields.float('Quantities', digits_compute= dp.get_precision('Product Unit of Measure')),
        'city': fields.many2one('res.city', 'City'),
        'no_of_days': fields.integer('No Of Days'),
        'product_id': fields.many2one('product.product', 'Product', domain=[('hr_expense_ok','=',True)]),
        'uom_id': fields.many2one('product.uom', 'Unit of Measure', required=True),
        'description': fields.text('Description'),
        'ref': fields.char('Reference', size=32),
        'sequence': fields.integer('Sequence', select=True, help="Gives the sequence order when displaying a list of expense lines."),
    
    }
    
    _defaults = {
        'no_of_days': 1,
        'date_value': lambda *a: time.strftime('%Y-%m-%d'),
        'uom_id': _get_uom_id,
    }
    _order = "sequence, date_value desc"
    
    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        res = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            res['name'] = product.name
            amount_unit = product.price_get('standard_price')[product.id]
            res['unit_amount'] = amount_unit
            res['uom_id'] = product.uom_id.id
        return {'value': res}

    def onchange_uom(self, cr, uid, ids, product_id, uom_id, context=None):
        res = {'value':{}}
        if not uom_id or not product_id:
            return res
        product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
        uom = self.pool.get('product.uom').browse(cr, uid, uom_id, context=context)
        if uom.category_id.id != product.uom_id.category_id.id:
            res['warning'] = {'title': _('Warning'), 'message': _('Selected Unit of Measure does not belong to the same category as the product Unit of Measure')}
            res['value'].update({'uom_id': product.uom_id.id})
        return res

hr_expense_planned()
    

class hr_expense_daily(osv.osv):
    _name = "hr.expense.daily"   
    
    def _amount(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}
        cr.execute("SELECT l.id,COALESCE(SUM(l.unit_amount-l.disallowed_amount),0) AS amount FROM hr_expense_daily l WHERE id IN %s GROUP BY l.id ",(tuple(ids),))
        res = dict(cr.fetchall())
        return res

    def _get_uom_id(self, cr, uid, context=None):
        result = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'product', 'product_uom_unit')
        return result and result[1] or False
    
    _columns = {
        'analytic_account': fields.many2one('account.analytic.account','Analytic account'),
        'date_value': fields.date('Expense From Date'),
        'name': fields.char('Description Of Expense', size=128, required=True),
        'expense_id': fields.many2one('hr.expense.expense', 'Expense', ondelete='cascade', select=True),
        'expense_to': fields.date('Expense To Date'),
        'invoice_date': fields.date('Invoice Date'),
        'invoice_no': fields.char('Invoice No.'),
        'uom_id': fields.many2one('product.uom', 'Unit of Measure'),         
        'attachment_file':fields.binary('Attachment'),
        'source': fields.char('Source'),
        'destination': fields.char('Destination'),
        'type_of_stay': fields.selection([('Lodging','Lodging (Hotel Accomodation)'),('Boarding','Boarding (Daily Allowance)')], "Type"),        
        'mode_of_travel': fields.selection([('Auto','Auto'),('Bus','Bus'),('Car','Car'),('Train','Train'),('Private Vehicle','Private Vehicle'),('Taxi','Taxi')], "Mode Of Travel"),        
        'total_amount': fields.function(_amount, string='Total', digits_compute=dp.get_precision('Account')),
        'disallowed_amount': fields.float('Disallowed Amount', digits_compute=dp.get_precision('Product Price')),
        'unit_amount': fields.float('Unit Price', digits_compute=dp.get_precision('Product Price')),
        'unit_quantity': fields.float('Qty', digits_compute= dp.get_precision('Product Unit of Measure')),
        'product_id': fields.many2one('product.product', 'Type Of Expense', domain=[('hr_expense_ok','=',True)]),
        'uom_id': fields.many2one('product.uom', 'Unit of Measure', required=True),
        'description': fields.text('Description'),
        'ref': fields.char('Reference', size=32),
        'sequence': fields.integer('Sequence', select=True, help="Gives the sequence order when displaying a list of expense lines."),
        'receipt_available': fields.selection([('Yes','Yes'),('No','No')], "Supporting Available", required=True),
        'supporting_date': fields.date('Date Of Supporting Doc', domain=[('receipt_available','=','Yes')]),
    }
    
    _defaults = {
        'uom_id': _get_uom_id,
        'unit_quantity': 1,
    }
    _order = "sequence, date_value"
            
    
    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        res = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            amount_unit = product.price_get('standard_price')[product.id]
            res['unit_amount'] = amount_unit
            res['uom_id'] = product.uom_id.id
        return {'value': res}

    def onchange_uom(self, cr, uid, ids, product_id, uom_id, context=None):
        res = {'value':{}}
        if not uom_id or not product_id:
            return res
        product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
        uom = self.pool.get('product.uom').browse(cr, uid, uom_id, context=context)
        if uom.category_id.id != product.uom_id.category_id.id:
            res['warning'] = {'title': _('Warning'), 'message': _('Selected Unit of Measure does not belong to the same category as the product Unit of Measure')}
            res['value'].update({'uom_id': product.uom_id.id})
        return res

hr_expense_daily()
    
    
class hr_expense_summary_report(osv.osv):
    _name = "hr.expense.summary.report"   
    
    
    
    _columns = {
        'serial_no': fields.integer('Sr. No.'),
        'product_name': fields.char('Type Of Expense'),
        'total_amount': fields.float('Total Amount', size=128, required=True),
        'frequency': fields.integer('Frequency'),
        'expense_id': fields.many2one('hr.expense.expense', 'Expense', ondelete='cascade', select=True),

        
    }
    
   
            
hr_expense_summary_report()
