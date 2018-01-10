from openerp.osv import fields, osv
from openerp.tools.translate import _
import base64
#from tools.translate import _
#from osv import osv, fields
import time
import datetime
from datetime import datetime
from datetime import date, timedelta
import os
import logging
from lxml import etree
from openerp.osv.orm import setup_modifiers
import binascii
from base64 import b64decode
from datetime import datetime, date
from lxml import etree
import time

from openerp import SUPERUSER_ID
from openerp import tools
from openerp.addons.resource.faces import task as Task


_logger = logging.getLogger(__name__)


class task_relation(osv.osv):
	_name = "task.relation"
	_description = "Task Dependencies"
	_columns = {
    		'name': fields.char('Task Name',size=80),
    		'parent_task_id': fields.many2one('project.task','Parent Task'),
    		'task_id': fields.many2one('project.task','Task'),
    		'project_id': fields.many2one('project.project','Project'),
    }

    # Inherits the create function for creating the record in task.relation table
	def create(self, cr, uid, vals, context=None):
		task_relation_id = super(task_relation, self).create(cr, uid, vals, context=context)
		new_task_ids = vals.get('task_id')
		o = self.pool.get('project.task').browse(cr,uid,new_task_ids)
		project_id = o.project_id.id
		self.write(cr,uid,task_relation_id,{'project_id':project_id})
		return task_relation_id


task_relation()



class project_state_type(osv.osv):
    _name = 'project.state.type'
    _description = 'Project Stage'
    _order = 'sequence'
    _columns = {
        'name': fields.char('Stage Name', required=True, translate=True),
        'description': fields.text('Description'),
        'sequence': fields.integer('Sequence'),
        'case_default': fields.boolean('Default for New Projects',
                        help="If you check this field, this stage will be proposed by default on each new project. It will not assign this stage to existing projects."),
        'project_ids': fields.many2many('project.project', 'project_task_type_rel1', 'type_id', 'project_id', 'Projects'),
        'fold': fields.boolean('Folded in Kanban View',
                               help='This stage is folded in the kanban view when'
                               'there are no records in that stage to display.'),
    }

    def _get_default_project_ids(self, cr, uid, ctx={}):
        project_id = self.pool['project.task']._get_default_project_id(cr, uid, context=ctx)
        if project_id:
            return [project_id]
        return None

    _defaults = {
        'sequence': 1,
        'project_ids': _get_default_project_ids,
    }
    _order = 'sequence'

project_state_type()

class project_task_type(osv.osv):
        _inherit = 'project.task.type'
        _columns={
                'task_stage_selection': fields.selection([('done', 'Done'),('onhold','Onhold'),('cancelled','Cancelled')],'Status Type'),
}

project_task_type()

class store_status(osv.osv):
	_name = "store.status"
	_description = "Store Status"
	_columns = {
    		'name': fields.char('Status',size=80),
    }

store_status()

class project(osv.osv):
	_inherit = 'project.project'
	_columns={
		'project_id': fields.many2one('project.project', 'Project', ondelete='set null', select=True, track_visibility='onchange', change_default=True),
		'stage_id': fields.many2one('project.task.type', 'Stage', track_visibility='onchange', select=True,domain="[('project_ids', '=', project_id)]", copy=False),
		'hr_employee_id': fields.many2one('hr.employee','Director of Sales'),
		'market_id': fields.many2one('market.place','Market'),
		'store_classification': fields.many2one('stores.type','Store Type'),
		'built_type': fields.many2one('store.status','Store Status'),
		'project_stage_id': fields.many2one('project.state.type', 'Stage', track_visibility='onchange', select=True,domain="[('project_ids', '=', project_id)]", copy=False),
		'project_type_ids': fields.many2many('project.state.type', 'project_task_type_rel1', 'project_id', 'type_id', 'Tasks Stages', states={'close':[('readonly',True)], 'cancelled':[('readonly',True)]}),
		
}

	def _get_type_project(self, cr, uid, context):
		ids = self.pool.get('project.state.type').search(cr, uid, [('case_default','=',1)], context=context)
		return ids

	_defaults={
		'project_type_ids': _get_type_project,
	}

	"""On change for the Director of Sales"""
	def onchange_hr_employee_id(self,cr,uid,ids,hr_employee_id):
		hr_obj = self.pool.get('hr.employee')
		if hr_employee_id == False:
			return {'value': {'market_id':''}}
		if hr_employee_id:
			hr_employee_data = hr_obj.browse(cr,uid,hr_employee_id)
			market_id = hr_employee_data.user_id.market_id.id
			return {'value': {'market_id':market_id}}
		return {}

	####CReating of the task onto the template button
	def map_tasks(self, cr, uid, old_project_id, new_project_id, context=None):
		""" copy and map tasks from old to new project """
		if context is None:
			context = {}
		map_task_id = {}
		map_dependencies_id={}
		task_obj = self.pool.get('project.task')
		task_relation_obj = self.pool.get('task.relation')
		proj = self.browse(cr, uid, old_project_id, context=context)
		for task in proj.tasks:
			# preserve task name and stage, normally altered during copy
			defaults = {'stage_id': task.stage_id.id,
						'name': task.name,
						}
			map_task_id[task.id] =  task_obj.copy(cr, uid, task.id, defaults, context=context)

		## section of code for tasks dependencies for wirelesss vision
		for x in task_relation_obj.search(cr, uid, [('project_id','=',old_project_id)]):
			cur_task_rel_obj = task_relation_obj.browse(cr, uid, x)
			if cur_task_rel_obj.parent_task_id.id in map_task_id.keys() and cur_task_rel_obj.task_id.id in map_task_id.keys():
				task_relation_obj.create(cr, uid, {	
					'name' : cur_task_rel_obj.name,
					'parent_task_id' : map_task_id[cur_task_rel_obj.parent_task_id.id],
					'task_id' : map_task_id[cur_task_rel_obj.task_id.id],
					'project_id' : new_project_id,

				})

		#### section ends here

		self.write(cr, uid, [new_project_id], {'tasks':[(6,0, map_task_id.values())]})
		task_obj.duplicate_task(cr, uid, map_task_id,context=context)
		return True

	###Creating the project from the Template
	def duplicate_template(self, cr, uid, ids, context=None):
		task_ids=[]
		context = dict(context or {})
		data_obj = self.pool.get('ir.model.data')
		task_obj = self.pool.get('project.type.task')
		result = []
		for proj in self.browse(cr, uid, ids, context=context):
			parent_id = context.get('parent_id', False)
			context.update({'analytic_project_copy': True})
			new_date_start = time.strftime('%Y-%m-%d')
			project_id = proj.id
			cr.execute("select type_id from project_task_type_rel1 where project_id = %s",(project_id,))
			project_ids = map(lambda x: x[0], cr.fetchall())
			cr.execute("select min(sequence) from project_state_type where id in %s",(tuple(project_ids),))
			sequence_ids = map(lambda x: x[0], cr.fetchall())
			cr.execute("select id from project_state_type where sequence = %s",(sequence_ids[0],))
			task_ids = map(lambda x: x[0], cr.fetchall())
			new_date_end = False
			if proj.date_start and proj.date:
				start_date = date(*time.strptime(proj.date_start,'%Y-%m-%d')[:3])
				end_date = date(*time.strptime(proj.date,'%Y-%m-%d')[:3])
				new_date_end = (datetime(*time.strptime(new_date_start,'%Y-%m-%d')[:3])+(end_date-start_date)).strftime('%Y-%m-%d')
			context.update({'copy':True})
			new_id = self.copy(cr, uid, proj.id, default = {
				'name':_("%s") % (proj.name),
				'state': 'open',
				'date_start':new_date_start,
				'date':new_date_end,
				'project_id': project_id,
				'project_stage_id': task_ids[0],
				'parent_id':parent_id}, context=context)
			result.append(new_id)
			child_ids = self.search(cr, uid, [('parent_id','=', proj.analytic_account_id.id)], context=context)
			parent_id = self.read(cr, uid, new_id, ['analytic_account_id'])['analytic_account_id'][0]
			if child_ids:
				self.duplicate_template(cr, uid, child_ids, context={'parent_id': parent_id})
		if result and len(result):
			res_id = result[0]
			form_view_id = data_obj._get_id(cr, uid, 'project', 'edit_project')
			form_view = data_obj.read(cr, uid, form_view_id, ['res_id'])
			tree_view_id = data_obj._get_id(cr, uid, 'project', 'view_project')
			tree_view = data_obj.read(cr, uid, tree_view_id, ['res_id'])
			search_view_id = data_obj._get_id(cr, uid, 'project', 'view_project_project_filter')
			search_view = data_obj.read(cr, uid, search_view_id, ['res_id'])
			return {
				'name': _('Projects'),
				'view_type': 'form',
				'view_mode': 'form,tree',
				'res_model': 'project.project',
				'view_id': False,
				'res_id': res_id,
				'views': [(form_view['res_id'],'form'),(tree_view['res_id'],'tree')],
				'type': 'ir.actions.act_window',
				'search_view_id': search_view['res_id'],
				'nodestroy': True
			}

	def create(self, cr, uid, vals, context=None):
		if context is None:
		    context = {}
		project_type_ids=vals.get('project_type_ids')
		values_project_type=project_type_ids[0][2][0]
		# Prevent double project creation when 'use_tasks' is checked + alias management
		create_context = dict(context, project_creation_in_progress=True,
		                      alias_model_name=vals.get('alias_model', 'project.task'),
		                      alias_parent_model_name=self._name)

		if vals.get('type', False) not in ('template', 'contract'):
		    vals['type'] = 'contract'

		project_id = super(project, self).create(cr, uid, vals, context=create_context)
		self.write(cr,uid,project_id,{'project_id': project_id,'project_stage_id':values_project_type})
		project_rec = self.browse(cr, uid, project_id, context=context)
		self.pool.get('mail.alias').write(cr, uid, [project_rec.alias_id.id], {'alias_parent_thread_id': project_id, 'alias_defaults': {'project_id': project_id}}, context)
		return project_id

project()

class task(osv.osv):
	_inherit= 'project.task'

	#########for making the boolean field active
	def _is_template(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		for task in self.browse(cr, uid, ids, context=context):
			res[task.id] = True
			if task.project_id:
				if task.project_id.active == False:
					res[task.id] = False
		return res

	_columns={
		'active': fields.function(_is_template, store=True, string='Not a Template Task', type='boolean', help="This field is computed automatically and have the same behavior than the boolean 'active' field: if the task is linked to a template or unactivated project, it will be hidden unless specifically asked."),
		'department_id': fields.many2one('hr.department','Department'),
		'project_state_id': fields.many2one('project.state.type','Project State'),
		'task_dependiencies': fields.one2many('task.relation','task_id','Task Dependencies'),
        'multiple_assigned_to': fields.many2many('res.users', 'assigned_to_users_rel', 'project_task_id', 'user_id', 'Assigned To'),
	}


	_defaults={
			'active': True,

	}

        def _check_dates(self, cr, uid, ids, context=None):
            if context == None:
                context = {}
            obj_task = self.browse(cr, uid, ids[0], context=context)
            start = obj_task.date_start or False
            end = obj_task.date_end or False
            if start and end :
                if start > end:
                    return False
            return True

        _constraints = [
            (_check_dates, "\nError ! Task End Date should be greater or less than today's Date.", ['date_start','date_end'])
        ]



	def onchange_deadline(self, cr, uid, ids, date_deadline, context=None):
		warning,value={},{}
		if date_deadline:
			todays_date = datetime.today().date()
			print "type type type",type(todays_date),type(date_deadline)
			if str(todays_date) > date_deadline:
				warning = {'title': _('Alert!'),'message' : _("You have entered wrong date. Deadline date must be greater than Todays Date")}
				value = {'date_deadline': ''}
		return {'warning': warning,'value': value}

	def duplicate_task(self, cr, uid, map_ids,context=None):
		mapper = lambda t: map_ids.get(t.id, t.id)
		for task in self.browse(cr, uid, map_ids.values(), context):
			# create_new_dependencies= task_relation_obj.create(cr,uid,task_defaults)
			new_child_ids = set(map(mapper, task.child_ids))
			new_parent_ids = set(map(mapper, task.parent_ids))
			if new_child_ids or new_parent_ids:
				task.write({'parent_ids': [(6,0,list(new_parent_ids))],
							'child_ids':  [(6,0,list(new_child_ids))]})

	# Inherits the create function for creating the record in task.relation table
	def create(self, cr, uid, vals, context=None):
		context = dict(context or {})

		# for default stage
		if vals.get('project_id') and not context.get('default_project_id'):
			context['default_project_id'] = vals.get('project_id')
		# user_id change: update date_start
		if vals.get('user_id') and not vals.get('date_start'):
			vals['date_start'] = fields.datetime.now()

		# context: no_log, because subtype already handle this
		create_context = dict(context, mail_create_nolog=True)
		task_id = super(task, self).create(cr, uid, vals, context=create_context)
		self._store_history(cr, uid, [task_id], context=context)
		return task_id

	###This function will give the laste index of the list
	def last_index(self,cr,uid,ids,context=None):
		return len(self)-1

	#inherits the write function for the task dependencies
	def write(self, cr, uid, ids, vals, context=None):
		if isinstance(ids, (int, long)):
			ids = [ids]

		# stage change: update date_last_stage_update
		if 'stage_id' in vals:
			vals['date_last_stage_update'] = fields.datetime.now()
			
			########code written for the task dependencies for the project
			main_task_id = ids[0]
			project_project_obj = self.pool.get('project.project')
			project_task_type_obj = self.pool.get('project.task.type')
			project_task_obj = self.pool.get('project.task')
			task_relation_obj = self.pool.get('task.relation')
			ir_model_data = self.pool.get('ir.model.data')
			task_relation_search = task_relation_obj.search(cr,uid,[('task_id','=',main_task_id)])
			if task_relation_search:
				for task_relation_id in task_relation_obj.browse(cr,uid,task_relation_search):
					parent_task_id = task_relation_id.parent_task_id.id
					state_name = self.browse(cr,uid,parent_task_id).stage_id.id
					state_selection = project_task_type_obj.browse(cr,uid,state_name).task_stage_selection
					if state_selection not in ('done','cancelled'):
						raise osv.except_osv(("Warning!"),("The Parent Task in the Task Dependencies is not completed."))
			##########code ends here

			################### code returns the current stage and the previous stage
			current_stage_id=vals.get('stage_id')
			current_project_id=self.browse(cr,uid,ids[0]).project_id.id
			cr.execute("select type_id from project_task_type_rel where project_id = %s",(current_project_id,))
			task_raise_stage_ids = map(lambda x: x[0], cr.fetchall())
			cr.execute("select sequence from project_task_type where id in %s",(tuple(task_raise_stage_ids),))
			sequence_raise_task_stage_ids = map(lambda x: x[0], cr.fetchall())
			current_stage_sequence=project_task_type_obj.browse(cr,uid,current_stage_id).sequence
			stage_read = self.read(cr, uid, ids, ['stage_id'], context=context)
			previous_stage_read = stage_read[0]['stage_id']
			previous_stage_read_id = previous_stage_read[0]
			previous_stage_sequence=project_task_type_obj.browse(cr,uid,previous_stage_read_id).sequence
			# previous_stage_sequence_admin = previous_stage_sequence+1
			user_id = context.get('uid')
			template_id = ir_model_data.get_object_reference(cr, uid, 'project', 'group_project_manager')[1]
			cr.execute("select uid from res_groups_users_rel where gid = %s",(template_id,))
			group_user_id = map(lambda x: x[0], cr.fetchall())
			previous_stage_sequence_index=sequence_raise_task_stage_ids.index(previous_stage_sequence)
			previous_stage_sequence_index_admin = previous_stage_sequence_index+1
			sequence_task_index = len(sequence_raise_task_stage_ids)-1
			if previous_stage_sequence_index_admin > sequence_task_index:
				pass
			else:
				next_stage_sequence = sequence_raise_task_stage_ids[previous_stage_sequence_index_admin]
				if user_id not in group_user_id and current_stage_sequence != next_stage_sequence:
					raise osv.except_osv(("Warning!"),("You cannot move directly to last state or previous state. Please Contact Administrator to give Group Access."))
				if user_id not in group_user_id and current_stage_sequence < previous_stage_sequence:
					raise osv.except_osv(("Warning!"),("You cannot move to the previous state. Please Contact Administrator."))
        	######################	


			#######code After closure of last Task automatically the phase should be turned into the other phase
			selection_ids_none = None
			task_main_id = self.browse(cr,uid,ids[0])
			task_project_id = task_main_id.project_id.id
			task_project_state_id = task_main_id.project_state_id.id
			cr.execute("select id from project_task where project_id = %s and project_state_id = %s",(task_project_id,task_project_state_id))
			task_ids = map(lambda x: x[0], cr.fetchall())
			task_ids.remove(main_task_id)
			if not task_ids:
				task_ids = ids
				cr.execute("select id from project_task where id in %s order by sequence desc",(tuple(task_ids),))
				sequence_ids = map(lambda x: x[0], cr.fetchall())
				stage_ids = [current_stage_id]
				cr.execute("select task_stage_selection from project_task_type where id in %s",(tuple(stage_ids),))
				selection_ids = map(lambda x: x[0], cr.fetchall())
			else:
				cr.execute("select id from project_task where id in %s order by sequence desc",(tuple(task_ids),))
				sequence_ids = map(lambda x: x[0], cr.fetchall())
				cr.execute("select stage_id from project_task where id in %s",(tuple(sequence_ids),))
				stage_ids = map(lambda x: x[0], cr.fetchall())
				cr.execute("select task_stage_selection from project_task_type where id in %s",(tuple(stage_ids),))
				selection_ids = map(lambda x: x[0], cr.fetchall())
			#####raise for the previous state task is not completed
			cr.execute("select type_id from project_task_type_rel1 where project_id = %s",(task_project_id,))
			project_raise_stage_ids = map(lambda x: x[0], cr.fetchall())
			cr.execute("select sequence from project_state_type where id in %s",(tuple(project_raise_stage_ids),))
			sequence_raise_project_stage_ids = map(lambda x: x[0], cr.fetchall())
			if task_project_state_id in project_raise_stage_ids:
				cr.execute("select sequence from project_state_type where id=%s",(task_project_state_id,))
				sequence_raise_main_stage_ids = map(lambda x: x[0], cr.fetchall())
				sequence_raise_stage_ids = sequence_raise_main_stage_ids[0]
				if sequence_raise_stage_ids in sequence_raise_project_stage_ids:
					sequence_raise_stage_ids = sequence_raise_stage_ids-1
					if sequence_raise_stage_ids in sequence_raise_project_stage_ids:
						cr.execute("select id from project_state_type where sequence = %s",(sequence_raise_stage_ids,))
						project_raise_write_stage_ids = map(lambda x: x[0], cr.fetchall())
						cr.execute("select stage_id from project_task where project_id=%s and project_state_id = %s",(task_project_id,project_raise_write_stage_ids[0]))
						raise_ids = map(lambda x: x[0], cr.fetchall())
						cr.execute("select task_stage_selection from project_task_type where id in %s",(tuple(raise_ids),))
						raise_selection_ids = map(lambda x: x[0], cr.fetchall())
						if raise_selection_ids[0] == None:
							raise osv.except_osv(("Warning!"),("The task of the previous state is not completed."))
			###################
			if selection_ids_none not in selection_ids:
				cr.execute("select type_id from project_task_type_rel1 where project_id = %s",(task_project_id,))
				project_stage_ids = map(lambda x: x[0], cr.fetchall())
				cr.execute("select sequence from project_state_type where id in %s",(tuple(project_stage_ids),))
				sequence_project_stage_ids = map(lambda x: x[0], cr.fetchall())
				if task_project_state_id in project_stage_ids:
					cr.execute("select sequence from project_state_type where id=%s",(task_project_state_id,))
					sequence_main_stage_ids = map(lambda x: x[0], cr.fetchall())
					sequence_stage_ids = sequence_main_stage_ids[0]
					if sequence_stage_ids in sequence_project_stage_ids:
						sequence_stage_ids = sequence_stage_ids+1
						if sequence_stage_ids in sequence_project_stage_ids:
							cr.execute("select id from project_state_type where sequence = %s",(sequence_stage_ids,))
							project_write_stage_ids = map(lambda x: x[0], cr.fetchall())
							project_stage_write_id = project_write_stage_ids[0]
							project_project_obj.write(cr,uid,task_project_id,{'project_stage_id':project_stage_write_id})
						else:
							sequence_stage_ids = sequence_stage_ids+1
							if sequence_stage_ids in sequence_project_stage_ids:
								cr.execute("select id from project_state_type where sequence = %s",(sequence_stage_ids,))
								project_write_stage_ids = map(lambda x: x[0], cr.fetchall())
								project_stage_write_id = project_write_stage_ids[0]
								project_project_obj.write(cr,uid,task_project_id,{'project_stage_id':project_stage_write_id})
			########


            ####code written for the assigned to will change the state
			cr.execute("select user_id from assigned_to_users_rel where project_task_id = %s",(main_task_id,))
			users_ids = map(lambda x: x[0], cr.fetchall())
			login_user_id = uid
			if login_user_id not in users_ids and login_user_id not in group_user_id:
				raise osv.except_osv(("Warning!"),("The Task is not assigned to you please check who is assigned."))
			elif login_user_id in group_user_id:
				pass

		# user_id change: update date_start
		if vals.get('user_id') and 'date_start' not in vals:
			vals['date_start'] = fields.datetime.now()

		# Overridden to reset the kanban_state to normal whenever
		# the stage (stage_id) of the task changes.
		if vals and not 'kanban_state' in vals and 'stage_id' in vals:
			new_stage = vals.get('stage_id')
			vals_reset_kstate = dict(vals, kanban_state='normal')
			for t in self.browse(cr, uid, ids, context=context):
				write_vals = vals_reset_kstate if t.stage_id.id != new_stage else vals
				super(task, self).write(cr, uid, [t.id], write_vals, context=context)
			result = True
		else:
			result = super(task, self).write(cr, uid, ids, vals, context=context)

		if any(item in vals for item in ['stage_id', 'remaining_hours', 'user_id', 'kanban_state']):
			self._store_history(cr, uid, ids, context=context)
		return result




task()

