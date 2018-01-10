import hashlib
import itertools
import logging
import os
import re
import pytz

from openerp import tools
from openerp.tools.translate import _
from openerp.exceptions import AccessError
from openerp.osv import fields,osv
from openerp import SUPERUSER_ID
from datetime import datetime, date, timedelta
from openerp.http import request, serialize_exception as _serialize_exception

from openerp import SUPERUSER_ID
import datetime
import time

_logger = logging.getLogger(__name__)


class ir_attachment_log(osv.osv):
    _name = 'ir.attachment.log'
    _columns = {
        'name':fields.char('File Name', readonly=True), 
        'user_id':fields.many2one('res.users','User', readonly=True),
        'write_date':fields.datetime('Modification', readonly=True),
        'download':fields.char('Download', readonly=True), 
        'ir_log_id':fields.many2one('ir.attachment','Attachment'),
    }    

    _defaults = {
        "write_date": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
    }
ir_attachment_log()    

class ir_attachment(osv.osv):
    _inherit = 'ir.attachment'


    def _file_read(self, cr, uid, fname, bin_size=False):
        full_path = self._full_path(cr, uid, fname)
        r = ''
        try:
            if bin_size:
                r = os.path.getsize(full_path)
            else:
                r = open(full_path,'rb').read().encode('base64')
        except IOError:
            _logger.exception("_read_file reading %s", full_path)
        return r
#####For saving file in hash format
    def _get_path(self, cr, uid, id, bin_data):
        # retro compatibility
        datas_fname_value = self.browse(cr, uid, id).datas_fname or False
        store_fname = self.browse(cr, uid, id).store_fname or False
        extension_value = ''
        if datas_fname_value:
            extension_len = datas_fname_value.rfind('.', 0, len(datas_fname_value))
            if extension_len:
                extension_value = datas_fname_value[extension_len:len(datas_fname_value)]
    ##### code to check if there's an extension for the attachment fetch it or else 
    ##### run the normal code
        if extension_value:
            sha = hashlib.sha1(bin_data).hexdigest()
            # retro compatibility
            fname = sha[:3] + '/' + sha + str(extension_value)
            full_path = self._full_path(cr, uid, fname)
            if os.path.isfile(full_path):
                return fname, full_path        # keep existing path
            # scatter files across 256 dirs
            # we use '/' in the db (even on windows)
            fname = sha[:2] + '/' + sha + str(extension_value)
            full_path = self._full_path(cr, uid, fname)
            if fname and full_path:
                _logger.error("File name of Uplaoded file %s and Full Path Of filestore  %s"%(fname,full_path))
            dirname = os.path.dirname(full_path)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
                os.chmod(dirname,0o777)
        else:
            sha = hashlib.sha1(bin_data).hexdigest()

            # retro compatibility
            fname = sha[:3] + '/' + sha
            full_path = self._full_path(cr, uid, fname)
            if os.path.isfile(full_path):
               return fname, full_path        # keep existing path

            # scatter files across 256 dirs
            # we use '/' in the db (even on windows)
            fname = sha[:2] + '/' + sha
            full_path = self._full_path(cr, uid, fname)
            dirname = os.path.dirname(full_path)
            if not os.path.isdir(dirname):
               os.makedirs(dirname)
               os.chmod(dirname,0o777)

        return fname, full_path

# ####For saving file as it is....
#     def _get_path(self, cr, uid, id, bin_data):
#         sha = hashlib.sha1(bin_data).hexdigest()

#         # retro compatibility
#         datas_fname_value = self.browse(cr, uid, id).datas_fname or False
#         # fname = sha[:3] + '/' + sha + '.pdf'
#         if datas_fname_value:
#             fname = datas_fname_value
#         else:
#             raise osv.except_osv(_('Error!'), _('Error occure while fetching datas_fname of file. \nKindly check file upload or contact to your administrator'))

#         full_path = self._full_path(cr, uid, fname)
#         if os.path.isfile(full_path):
#             return fname, full_path        # keep existing path

#         # scatter files across 256 dirs
#         # we use '/' in the db (even on windows)
#         fname = datas_fname_value
#         full_path = self._full_path(cr, uid, fname)
#         if fname and full_path:
#             _logger.error("File name of Uplaoded file %s and Full Path Of filestore  %s"%(fname,full_path))
#         dirname = os.path.dirname(full_path)
#         if not os.path.isdir(dirname):
#             os.makedirs(dirname)
#             os.chmod(dirname,0o777)
#         else:
#             sha = hashlib.sha1(bin_data).hexdigest()

#             # retro compatibility
#             fname = sha[:3] + '/' + sha
#             full_path = self._full_path(cr, uid, fname)
#             if os.path.isfile(full_path):
#                return fname, full_path        # keep existing path

#             # scatter files across 256 dirs
#             # we use '/' in the db (even on windows)
#             fname = sha[:2] + '/' + sha
#             full_path = self._full_path(cr, uid, fname)
#             dirname = os.path.dirname(full_path)
#             if not os.path.isdir(dirname):
#                os.makedirs(dirname)
#                os.chmod(dirname,0o777)
#         return fname, full_path

    def _full_path(self, cr, uid, path):
        # sanitize ath
        # path = re.sub('[.]', '', path)
        path = path.strip('/\\')
        return os.path.join(self._filestore(cr, uid), path)


    def _file_write(self, cr, uid, id, value):
        bin_value = value.decode('base64')
        fname, full_path = self._get_path(cr, uid, id, bin_value)
        if not os.path.exists(full_path):
            try:
                with open(full_path, 'wb') as fp:
                    fp.write(bin_value)
            except IOError:
                _logger.exception("_file_write writing %s", full_path)
        return fname

    def _data_set(self, cr, uid, id, name, value, arg, context=None):
        # We dont handle setting data to null
        if not value:
            return True
        if context is None:
            context = {}
        location = self._storage(cr, uid, context)
        file_size = len(value.decode('base64'))
        attach = self.browse(cr, uid, id, context=context)
#        fname_to_delete = attach.store_fname
        if location != 'db':
            fname = self._file_write(cr, uid, id, value)
            # SUPERUSER_ID as probably don't have write access, trigger during create
            super(ir_attachment, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size, 'db_datas': False}, context=context)
        else:
            super(ir_attachment, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size, 'store_fname': False}, context=context)

        # After de-referencing the file in the database, check whether we need
        # to garbage-collect it on the filesystem
#        if fname_to_delete:
#            self._file_delete(cr, uid, fname_to_delete)
        return True   

    def _data_get(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        bin_size = context.get('bin_size')
        for attach in self.browse(cr, uid, ids, context=context):
            if attach.store_fname:
                result[attach.id] = self._file_read(cr, uid, attach.store_fname, bin_size)
            else:
                result[attach.id] = attach.db_datas
        return result     

    _columns = {
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='File Content', type="binary", nodrop=True),
        'admin_doc_access': fields.char('Admin Access', help="This Fields give the access of directory to admin also"), 
        're_groups_doc_rel':fields.many2many('res.groups','re_doc_res_group_rel','docid','gid',"Read Groups"),
        're_users_doc_rel':fields.many2many('res.users','re_doc_res_users_rel','docid','users_id',"Read users"),
        're_job_doc_rel':fields.many2many('hr.job','re_job_doc_rel','docid','jobid',"Job Positions"),
        'un_groups_doc_rel':fields.many2many('res.groups','un_doc_res_group_rel','docid','gid',"Unlink Group"),
        'un_users_doc_rel':fields.many2many('res.users','un_doc_res_users_rel','docid','users_id',"Unlink Users"),
        'wr_groups_doc_rel':fields.many2many('res.groups','wr_doc_res_group_rel','docid','gid',"Write Group"),
        'wr_users_doc_rel':fields.many2many('res.users','wr_doc_res_users_rel','docid','users_id',"Write Users"),
        'log_ids': fields.one2many('ir.attachment.log', 'ir_log_id', 'Log lines'),
        'attachment_url':fields.char('URL', help="This is an URL of documents"),
        'intranet_check':fields.boolean('Intranet'),
        'publish_start_date':fields.date('Publish Start Date'),
        'publish_end_date':fields.date('Publish End Date'),
        # 'cr_url':fields.function(_get_url, type='char', string='Url'),
        # 'has_logs': fields.function(_has_logs, type="boolean"),
        
    }
    _defaults = {
                'admin_doc_access':1,
    } 

#####Function to send document date WordPress for Json Feed
#    def wordpress_documents_data(self, cr, uid, context=None):
#   current_date = datetime.datetime.now()
#        ir_attachment_ids = self.search(cr,uid,[('intranet_check','=',True),('publish_start_date','<=',current_date),('publish_end_date','>=',current_date)])
#        att_ids = []
#        if ir_attachment_ids:
#            for ir_attachment_id in ir_attachment_ids:
#                attachment_name = self.browse(cr,uid,ir_attachment_id).name or False
#                attachment_url = self.browse(cr,uid,ir_attachment_id).attachment_url or False
#       cr.execute('select name from res_groups where wordpress_active = True and id in (select gid from re_doc_res_group_rel where docid = %s)'%(ir_attachment_id))
#       attachment_group = map(lambda x: x[0], cr.fetchall())
#       attachment_group = 'subscriberrsa'
#       if attachment_name and attachment_url and attachment_group:
#                    att_ids.append([attachment_name,attachment_url,attachment_group[0]])
#        return att_ids

#####Inherit create      
    def create(self, cr, uid, vals, context=None):
#        _logger.error("context ***** :%s, vals**************** :%s"%(context, vals))        
        doc_dir_obj = self.pool.get('document.directory')
        res_groups_obj = self.pool.get('res.groups')
        res_users_obj = self.pool.get('res.users')
        hr_employee_obj = self.pool.get('hr.employee')
        dms_config_obj = self.pool.get('dms.config')

        directory_name = ''        

        intranet_check_vals = vals.get('intranet_check',False)
        publish_start_date = vals.get('publish_start_date',False)
        publish_end_date = vals.get('publish_end_date',False)  
        self._documents_attachments_raise(cr,uid,vals,context)
        self._task_document_attachment_raise(cr,uid,vals,context)      
        res = super(ir_attachment, self).create(cr, uid, vals, context=context)
        self._documents_access_rights(cr,uid,vals,res,context)
        self._task_documents_access_rights(cr,uid,vals,res,context)
        if publish_start_date and publish_end_date and publish_start_date > publish_end_date:
            raise osv.except_osv(_('Access Denied!'), _('Publish Start Date must be greater than Publish End Date.\nPlease check Published Start Date and End Date you have entered.'))


        if context and uid != 1:
            uid_job_id = False
            if uid:
                uid_login = res_users_obj.browse(cr,uid,uid).login or False
                if uid_login:
                    emp_ids = hr_employee_obj.search(cr,uid,[('emp_no','=',uid_login)])
                    if emp_ids:
                        uid_job_id = hr_employee_obj.browse(cr,uid,emp_ids).job_id.id or False

        #####Get the directory id from context
            if 'active_model' in context:
                active_model = context.get('active_model')
                if active_model == 'document.directory':
                    if 'active_id' in context:
                        dir_id = context.get('active_id')
                    elif 'active_ids' in context:
                        dir_ids = context.get('active_ids')
                        if dir_ids:
                            dir_id = dir_ids[0]
                #####If get the directory id in context
                    if dir_id:
                    #####Get the user's id from directory create page
                        cr.execute('select users_id from cr_dir_res_users_rel where dirid = %s'%(dir_id))
                        cr_dir_res_users_ids = map(lambda x: x[0], cr.fetchall())
                    #####If match not found in users it'll search into groups
                    #####Get the group from directory
                        cr.execute('select gid from cr_dir_res_group_rel where dirid = %s'%(dir_id))
                        cr_dir_res_group_ids = map(lambda x: x[0], cr.fetchall())
                    #####Get job id
                        cr.execute('select jobid from cr_job_dir_rel where dirid = %s'%(dir_id))
                        cr_job_dir_ids = map(lambda x: x[0], cr.fetchall())
                        cr.execute('select jobid from re_job_dir_rel where dirid = %s'%(dir_id))
                        re_job_dir_ids = map(lambda x: x[0], cr.fetchall())
                        cr.execute('select jobid from re_job_doc_rel where docid = %s'%(res))
                        re_job_doc_ids = map(lambda x: x[0], cr.fetchall())
                        
                        if re_job_doc_ids and re_job_dir_ids and len(list(set(re_job_doc_ids).intersection(re_job_dir_ids))) != len(re_job_doc_ids):
                                raise osv.except_osv(_('Warning'),_("You have entered such Job Position in document which don't have read access of this directory."))
                        elif re_job_dir_ids and cr_job_dir_ids and len(list(set(cr_job_dir_ids).intersection(re_job_dir_ids))) != len(cr_job_dir_ids):
                                raise osv.except_osv(_('Warning'),_("You have entered such Create Job Position in directory which don't have read access of this directory."))

                    #####Checked the users access rights
                        if not cr_dir_res_group_ids and not cr_dir_res_users_ids and not cr_job_dir_ids:
                            pass
                        elif cr_dir_res_users_ids and uid in cr_dir_res_users_ids:
                        #####If found match it'll allow to create documents
                            pass
                        elif cr_job_dir_ids and uid_job_id and uid_job_id in cr_job_dir_ids:
                            pass
                        elif cr_dir_res_group_ids:
                        #####Get the groups from user's master
                            cr.execute('select gid from res_groups_users_rel where uid = %s'%(uid))
                            res_groups_users_ids = map(lambda x: x[0], cr.fetchall())
                        #####Checked user is exist in directory groups
                        #####If yes, it'll allowed to create documents
                        #####else it'll restricted to the user
                            if res_groups_users_ids and list(set(res_groups_users_ids).intersection(cr_dir_res_group_ids)):
                                pass
                            else:
                                raise osv.except_osv(_('Access Denied!'), _('You are not allowed to create this record. \nKindly check Directory Create Access Rights Configuration or contact to your administrator'))
                        else:
                            raise osv.except_osv(_('Access Denied!'), _('You are not allowed to create this record. \nKindly Check Directory Create Access Configuration or contact to your administrator'))
        vals.update({
            'index_content': '',
        })

        # self._documents_attachments_raise(cr,uid,vals,context)
        # self._task_document_attachment_raise(cr,uid,vals,context)
        # self._documents_access_rights(cr,uid,vals,res,context)
        # self._task_documents_access_rights(cr,uid,vals,res,context)

#        if intranet_check_vals:
#            cr.execute("select name from res_groups where wordpress_active = True and id in (select gid from re_doc_res_group_rel where docid = %s)"%(str(res)))
#            attachment_group = map(lambda x: x[0], cr.fetchall())
#            if attachment_group and len(attachment_group) > 1:
#                raise osv.except_osv(_('Access Denied!'), _('You are selected more than one wordpress groups.\nKnidly select only one WordPress group.\nKindly check configuration or contact to your administrator'))
#            elif not attachment_group:
#                raise osv.except_osv(_('Access Denied!'), _("You are Checked Intranet option & didn't select WordPress Group.\nKnidly select only one WordPress group.\nKindly check configuration or contact to your administrator"))

        store_fname_value = self.browse(cr,uid,res).store_fname or False
        if request:
            host_url = request.httprequest.host_url
        else:
            host_url = False
        dms_config_ids = dms_config_obj.search(cr,uid,[('active','=',True)])

        if dms_config_ids:
            dms_config_data = dms_config_obj.browse(cr,uid,dms_config_ids[0])
            directory_name = dms_config_data.directory_name or ''
            attachment_path = dms_config_data.attachment_path or ''


            if not directory_name or not attachment_path:
                raise osv.except_osv(_('Warning'),_("Check the DMS configuration. Directory is not set"))
        else:
            raise osv.except_osv(_('Warning'),_("Check the DMS configuration"))

        # link_url = 'base/static/img/odoo_testing/odoo8-training/'+str(directory_name) + str(store_fname_value)
        link_url = str(attachment_path)+str(directory_name) + str(store_fname_value)
        link_url = link_url.replace("//", "/");
        link_url = str(host_url)+str(link_url)

        if link_url and res:
            # cr.execute("update ir_attachment set index_content = null,db_datas = null,attachment_url = %s where id in %s",(str(link_url),tuple(res)))
            self.write(cr,uid,res,{'attachment_url':str(link_url)})
        return res

        ####code writen for the uploading of the attachments into the project only by team members
    def _documents_attachments_raise(self,cr,uid,vals,context):
        project_project_obj = self.pool.get('project.project')
        res_id_values = vals.get('res_id')
        res_model_values = vals.get('res_model')
        if res_model_values == 'project.project':
            main_user_id = uid
            project_project_id = project_project_obj.browse(cr,uid,res_id_values)
            project_main_id = project_project_id.id
            cr.execute('select uid from project_user_rel where project_id=%s',(project_main_id,))
            document_user_id = map(lambda x: x[0], cr.fetchall())
            if main_user_id not in document_user_id:
                raise osv.except_osv(('Warning!'),('You are not allowed to upload the attachment Because You are not a team member'))
        return True

#######Code written to put the project files into the Projet Folder###
    def _documents_access_rights(self,cr,uid,vals,res,context):
        #code writen for the groups accessrights for the documents of project from the department master
        # doc_dir_obj = self.pool.get('document.directory')
        # project_task_obj = self.pool.get('project.task')
        # res_id_values = vals.get('res_id')
        # project_task_id = project_task_obj.browse(cr,uid,res_id_values)
        # project_task_department = project_task_id.department_id.id
        # cr.execute('select groups_id from department_groups_rel where department_id=%s',(project_task_department,))
        # department_group_id = map(lambda x: x[0], cr.fetchall())
        # for job_group_insert_id in department_group_id:
        #     cr.execute('insert into re_doc_res_group_rel (docid,gid) values(%s,%s)',(res,job_group_insert_id))
        ######code writen for the access rights for the main project attachment
        if context is None:
            context = {}
        doc_dir_obj = self.pool.get('document.directory')
        project_project_obj = self.pool.get('project.project')
        res_id_values = vals.get('res_id')
        res_model_values = vals.get('res_model')
        if res_model_values == 'project.project':
            project_project_id = project_project_obj.browse(cr,uid,res_id_values)
            project_main_id = project_project_id.id
            cr.execute('select uid from project_user_rel where project_id=%s',(project_main_id,))
            document_user_id = map(lambda x: x[0], cr.fetchall())
            for document_user_insert_id in document_user_id:
                cr.execute('insert into re_doc_res_users_rel (docid,users_id) values(%s,%s)',(res,document_user_insert_id))
        #######Code written to put the project files into the Projet Folder###
        active_model = context.get('active_model')
        parent_id = context.get('parent_id')
        model_values = 'project.project'
        if active_model == 'document.directory':
            cr.execute('update ir_attachment set parent_id=%s where id =%s',(parent_id,res))
       # else:
       #     cr.execute('select id from ir_model where model=%s',(model_values,))
       #     model_id = map(lambda x: x[0], cr.fetchall())
       #     print "sdasdsadsaasdasdddsadsad",model_id
       #     cr.execute('select id from document_directory where model_id=%s',(model_id[0],))
       #     document_id = map(lambda x: x[0], cr.fetchall())
       #     print "ddadsds",document_id
       #     if document_id[0]:
       #         cr.execute('update ir_attachment set parent_id=%s where id =%s',(document_id[0],res))
        return True

####### code writen for the task documents access to the assignedto,reviewer,projectmanager
    def _task_documents_access_rights(self,cr,uid,vals,res,context):
        list_task_members = []
        project_task_obj = self.pool.get('project.task')
        res_id_values = vals.get('res_id')
        res_model_values = vals.get('res_model')
        if res_model_values == 'project.task':
            project_task_id = project_task_obj.browse(cr,uid,res_id_values)
            project_task_main_id = project_task_id.id
            cr.execute('select user_id from assigned_to_users_rel where project_task_id=%s',(project_task_main_id,))
            task_document_user_id = map(lambda x: x[0], cr.fetchall())
            for task_assigned_to in task_document_user_id:
                cr.execute('insert into re_doc_res_users_rel (docid,users_id) values(%s,%s)',(res,task_assigned_to))
            ####code writen for the assigned to reviewer,project_manager to document upload
            # task_assigned_to = project_task_id.user_id.id
            # task_reviewer_id = project_task_id.reviewer_id.id
            # task_project_manager_id = project_task_id.project_id.user_id.id
            # list_task_members.append([task_assigned_to,task_reviewer_id,task_project_manager_id])
            # list_task_members_id = list_task_members[0]
            # for list_task_id in list_task_members_id:
            #     cr.execute('insert into re_doc_res_users_rel (docid,users_id) values(%s,%s)',(res,list_task_id))
        return True

    ####code writen for the uploading of the attachments into the task only by assignedto,reviewer,projectmanager
    def _task_document_attachment_raise(self,cr,uid,vals,context):
        list_task_members = []
        project_task_obj = self.pool.get('project.task')
        res_id_values = vals.get('res_id')
        res_model_values = vals.get('res_model')
        if res_model_values == 'project.task':
            main_user_id = uid
            project_task_id = project_task_obj.browse(cr,uid,res_id_values)
            project_task_main_id = project_task_id.id
            cr.execute('select user_id from assigned_to_users_rel where project_task_id=%s',(project_task_main_id,))
            task_document_user_id = map(lambda x: x[0], cr.fetchall())
            if main_user_id not in task_document_user_id:
                raise osv.except_osv(('Warning!'),('You are not allowed to upload the attachment Because You are not a team member'))
            ###code written for uploading of the attachments into the task only
            # task_assigned_to = project_task_id.user_id.id
            # task_reviewer_id = project_task_id.reviewer_id.id
            # task_project_manager_id = project_task_id.project_id.user_id.id
            # list_task_members.append([task_assigned_to,task_reviewer_id,task_project_manager_id])
            # list_task_members_id = list_task_members[0]
            # if main_user_id not in list_task_members_id:
            #     raise osv.except_osv(('Warning!'),('You are not allowed to upload the attachment Because You are not a team member'))
        return True        

    def write(self, cr, uid, ids, vals, context=None):
        doc_dir_obj = self.pool.get('document.directory')
        res_groups_obj = self.pool.get('res.groups')
        res_users_obj = self.pool.get('res.users')
        hr_employee_obj = self.pool.get('hr.employee')
        dms_config_obj = self.pool.get('dms.config')
        ir_log_obj = self.pool.get('ir.attachment.log')

        if isinstance(ids, (int, long)):
            ids = [ids]
        self_data = self.browse(cr,uid,ids)
        user_id = uid        
        datas_fname_val = self_data.datas_fname or False
        download = self_data.attachment_url or False
        if 'intranet_check' in vals:
            intranet_check_vals = vals['intranet_check']
        else:
            intranet_check_vals = self_data.intranet_check or False

        if 'publish_start_date' in vals:
            publish_start_date = vals['publish_start_date']
        else:
            publish_start_date = self_data.publish_start_date or False

        if 'publish_end_date' in vals:
            publish_end_date = vals['publish_end_date']
        else:
            publish_end_date = self_data.publish_end_date or False

        if publish_start_date and publish_end_date and publish_start_date > publish_end_date:
            raise osv.except_osv(_('Access Denied!'), _('Publish Start Date in document must be greater than Publish End Date.\nPlease check Published Start Date and End Date you have entered.'))

        if 'datas' in vals and download and datas_fname_val and user_id and ids:
            ir_log_obj.create(cr,uid,{'download':download,'name':datas_fname_val,'user_id':user_id,'write_date':datetime.datetime.now(),'ir_log_id':ids[0]})

        directory_name = ''        

        if context and uid != 1:
            uid_job_id = False
            if uid:
                uid_login = res_users_obj.browse(cr,uid,uid).login or False
                if uid_login:
                    emp_ids = hr_employee_obj.search(cr,uid,[('emp_no','=',uid_login)])
                    if emp_ids:
                        uid_job_id = hr_employee_obj.browse(cr,uid,emp_ids).job_id.id or False

        #####Get the directory id from context
            if 'active_model' in context:
                active_model = context.get('active_model')
                if active_model == 'document.directory':
                    if 'active_id' in context:
                        dir_id = context.get('active_id')
                    elif 'active_ids' in context:
                        dir_ids = context.get('active_ids')
                        if dir_ids:
                            dir_id = dir_ids[0]
                #####If get the directory id
                    if dir_id:
                    #####Get the user's id from directory write page 
                        cr.execute('select users_id from wr_dir_res_users_rel where dirid = %s'%(dir_id))
                        wr_dir_res_users_ids = map(lambda x: x[0], cr.fetchall())
                    #####If match not found in users it'll search into groups
                    #####Get the group from directory                            
                        cr.execute('select gid from wr_dir_res_group_rel where dirid = %s'%(dir_id))
                        wr_dir_res_group_ids = map(lambda x: x[0], cr.fetchall())                        
                    #####Checked the users access rights
                        cr.execute('select jobid from wr_job_dir_rel where dirid = %s'%(dir_id))
                        wr_job_dir_ids = map(lambda x: x[0], cr.fetchall())

                        cr.execute('select jobid from re_job_dir_rel where dirid = %s'%(dir_id))
                        re_job_dir_ids = map(lambda x: x[0], cr.fetchall())
                        cr.execute('select jobid from re_job_doc_rel where docid = %s'%(ids[0]))
                        re_job_doc_ids = map(lambda x: x[0], cr.fetchall())
                        
                        if re_job_doc_ids and re_job_dir_ids and len(list(set(re_job_doc_ids).intersection(re_job_dir_ids))) != len(re_job_doc_ids):
                                raise osv.except_osv(_('Warning'),_("You have entered such Job Position in document which don't have read access of this directory."))
                        elif re_job_dir_ids and wr_job_dir_ids and len(list(set(wr_job_dir_ids).intersection(re_job_dir_ids))) != len(wr_job_dir_ids):
                                raise osv.except_osv(_('Warning'),_("You have entered such Create Job Position in directory which don't have read access of this directory."))

                        if not wr_dir_res_users_ids and not wr_dir_res_group_ids and not wr_job_dir_ids:
                            pass
                        elif wr_dir_res_users_ids and uid in wr_dir_res_users_ids:
                        #####If found match it'll allow to edit documents                            
                            pass
                        elif wr_job_dir_ids and uid_job_id and uid_job_id in wr_job_dir_ids:
                            pass
                        elif wr_dir_res_group_ids:
                            #####Get the groups from user's master                                
                                cr.execute('select gid from res_groups_users_rel where uid = %s'%(uid))
                                res_groups_users_ids = map(lambda x: x[0], cr.fetchall())
                            #####Checked user is exist in directory groups
                            #####If yes, it'll allowed to edit documents
                            #####else it'll restricted to the user                                
                                if res_groups_users_ids and list(set(res_groups_users_ids).intersection(wr_dir_res_group_ids)):
                                    pass
                                else:
                                    raise osv.except_osv(_('Access Denied!'), _('You are not allowed to edit this record. \nKindly check directory Edit Rights Configuration or contact to your administrator'))
                        else:
                            raise osv.except_osv(_('Access Denied!'), _('You are not allowed to edit this record. \nKindly check directory edit rights configuration or contact to your administrator'))
        vals.update({
                    'index_content': '',
                }) 
        res = super(ir_attachment, self).write(cr, uid, ids, vals, context=context)

#        if intranet_check_vals:
#            cr.execute("select name from res_groups where wordpress_active = True and id in (select gid from re_doc_res_group_rel where docid = %s)"%(str(ids[0])))
#            attachment_group = map(lambda x: x[0], cr.fetchall())
#            if attachment_group and len(attachment_group) > 1:
#                raise osv.except_osv(_('Access Denied!'), _('You are selected more than one wordpress groups.\nKnidly select only one WordPress group.\nKindly check configuration or contact to your administrator'))
#            elif not attachment_group:
#                raise osv.except_osv(_('Access Denied!'), _("You are Checked Intranet option & didn't select WordPress Group.\nKnidly select only one WordPress group.\nKindly check configuration or contact to your administrator"))

    #####Start - Update URL in attachment_url  field
        if context:
            store_fname_value = self_data.store_fname or False
            host_url = request.httprequest.host_url
            dms_config_ids = dms_config_obj.search(cr,uid,[('active','=',True)])

            if dms_config_ids:
                dms_config_data = dms_config_obj.browse(cr,uid,dms_config_ids[0])
                directory_name = dms_config_data.directory_name or ''
                attachment_path = dms_config_data.attachment_path or ''
                if not directory_name or not attachment_path:
                    raise osv.except_osv(_('Warning'),_("Check the DMS configuration. Directory is not set"))
            else:
                raise osv.except_osv(_('Warning'),_("Check the DMS configuration"))        
            link_url = str(attachment_path)+str(directory_name) + str(store_fname_value)
            # link_url = 'base/static/img/odoo_testing/odoo8-training/'+str(directory_name) + str(store_fname_value)
            link_url = link_url.replace("//", "/");
            link_url = str(host_url)+str(link_url)
            if link_url and ids:
                # cr.execute("update ir_attachment set index_content = null,db_datas = null,attachment_url = %s  where id = %s",(str(link_url),str(ids[0])))
                self.write(cr,uid,ids,{'attachment_url':str(link_url)})
    #####End - Update URL in attachment_url  field
            
        return res     

    def get_url(self, cr, uid, ids, context=None):
        
        host_url = request.httprequest.host_url
        ir_actions_obj = self.pool.get('ir.actions.actions')
        ir_actions_ids = ir_actions_obj.search(cr,uid,[('name','=','Directory'),('type','=','ir.actions.act_window')])
        active_id = ''
        if context and "active_id" in context:
            active_id = context.get('active_id')

        if host_url and ids and ir_actions_ids and active_id:
            url = host_url+'web#id='+str(ids[0])+'&view_type=form&model=ir.attachment&action='+str(ir_actions_ids[0])+'&active_id='+str(active_id)
            raise osv.except_osv(_('Browser URL'), _(url))
        elif host_url and ids and active_id:
            url = host_url+'web#id='+str(ids[0])+'&view_type=form&model=ir.attachment&active_id='+str(active_id)
            raise osv.except_osv(_('Browser URL'), _(url))
        else:
            raise osv.except_osv(_('Alert'), _("Something went wrong while fetching URL. Copy URL directly from browser or else contact your administrator"))

        return True

    def unlink(self, cr, uid, ids, context=None):
        doc_dir_obj = self.pool.get('document.directory')
        res_groups_obj = self.pool.get('res.groups')
        res_users_obj = self.pool.get('res.users')
        hr_employee_obj = self.pool.get('hr.employee')
        
        if context and uid != 1:
            uid_job_id = False
            if uid:
                uid_login = res_users_obj.browse(cr,uid,uid).login or False
                if uid_login:
                    emp_ids = hr_employee_obj.search(cr,uid,[('emp_no','=',uid_login)])
                    if emp_ids:
                        uid_job_id = hr_employee_obj.browse(cr,uid,emp_ids).job_id.id or False

        #####Get the directory id from context
            if 'active_model' in context:
                active_model = context.get('active_model')
                if active_model == 'document.directory':
                    if 'active_id' in context:
                        dir_id = context.get('active_id')
                    elif 'active_ids' in context:
                        dir_ids = context.get('active_ids')
                        if dir_ids:
                            dir_id = dir_ids[0]
                #####If get the directory id
                    if dir_id:
                    #####Get the user's id from directory unlink page 
                        cr.execute('select users_id from un_dir_res_users_rel where dirid = %s'%(dir_id))
                        un_dir_res_users_ids = map(lambda x: x[0], cr.fetchall())
                    #####Get the group from directory                              
                        cr.execute('select gid from un_dir_res_group_rel where dirid = %s'%(dir_id))
                        un_dir_res_group_ids = map(lambda x: x[0], cr.fetchall())

                        cr.execute('select jobid from un_job_dir_rel where dirid = %s'%(dir_id))
                        un_job_dir_ids = map(lambda x: x[0], cr.fetchall())

                    #####Checked the users access rights
                        if not un_dir_res_group_ids and not un_dir_res_users_ids and not un_job_dir_ids:
                            raise osv.except_osv(_('Access Denied!'), _('You are not allowed to delete this record. \nKindly check configuration or contact to your administrator'))
                            # pass
                        elif un_dir_res_users_ids and uid in un_dir_res_users_ids:
                        #####If found match it'll allow to delete documents                            
                            pass
                        elif un_job_dir_ids and uid_job_id and uid_job_id in un_job_dir_ids:
                            pass
                        elif un_dir_res_group_ids:
                            #####Get the groups from user's master                                  
                                cr.execute('select gid from res_groups_users_rel where uid = %s'%(uid))
                                res_groups_users_ids = map(lambda x: x[0], cr.fetchall())
                            #####Checked user is exist in directory groups
                            #####If yes, it'll allowed to delete documents
                            #####else it'll restricted to the user                                    
                                if res_groups_users_ids and list(set(res_groups_users_ids).intersection(un_dir_res_group_ids)):
                                    pass
                                else:
                                    raise osv.except_osv(_('Access Denied!'), _('You are not allowed to delete this record. \nKindly check directory delete access rights configuration or contact to your administrator'))
                        else:
                            raise osv.except_osv(_('Access Denied!'), _('You are not allowed to delete this record. \nKindly check directory delete access rights configuration or contact to your administrator'))

        res = super(ir_attachment, self).unlink(cr, uid, ids, context)
        return res  

######cofig_path function get a path form class cofig_path and validate it
    @tools.ormcache(skiparg=3)
    def cofig_path(self, cr, uid, context=None):
        obj_cofig_path = self.pool.get("dms.config")
        path_id =  obj_cofig_path.search(cr, uid, [('active', '=', True)], context=context)

        if path_id and len(path_id) == 1:
            file_path = obj_cofig_path.browse(cr,uid,path_id).file_path
            dir_path = obj_cofig_path.browse(cr,uid,path_id).directory_name
            if not dir_path.startswith('/'):
                dir_path = '/'+dir_path
            path = file_path + dir_path
            path = path.replace("//", "/")
            if not path.endswith('/'):
                path=path+"/"
        else:
            raise osv.except_osv(_('Warning!'), _('File Path is not configured. Set File path or else contact to your administrator'))
        return path

######def _filestore function is inherited function of class ir_attachment and gets a path from def cofig_path and return it
    @tools.ormcache(skiparg=3)    
    def _filestore(self, cr, uid, context=None):
        path = self.cofig_path(cr, uid, context=None);
        _logger.error("File mported at %s",path)
        return path

ir_attachment()


#----------------------------------------------------------
# change directory wizard
#----------------------------------------------------------

class change_directory_wizard(osv.TransientModel):
    """
        A wizard to manage the change of documents directory
    """

    _name = "change.directory.wizard"
    _description = "Change Directory Wizard"
    _columns = {
        'document_ids': fields.one2many('change.directory.document', 'wizard_id', string='Document'),
        'move_all':fields.boolean('Move All Into One Directory'),
        'directory_id': fields.many2one('document.directory','Directory'),

    }

    def _default_attach_ids(self, cr, uid, context=None):
        if context is None:
            context = {}
        ir_attach_model = self.pool['ir.attachment']
        ir_attach_ids = context.get('active_model') == 'ir.attachment' and context.get('active_ids') or []
        return [
            (0, 0, {'document_id': attachment.id})
            for attachment in ir_attach_model.browse(cr, uid, ir_attach_ids, context=context)
        ]

    _defaults = {
        'document_ids': _default_attach_ids,
        'move_all':True,
    }

    def change_directory_button(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids, context=context)[0]
        move_all_value = wizard.move_all
        if move_all_value:
            need_reload = any(id == attachment.id for attachment in wizard.document_ids)
            line_ids = [attachment.id for attachment in wizard.document_ids]
            context.update({'directory_id':wizard.directory_id.id})
            self.pool.get('change.directory.document').change_moveall_directory_button(cr, uid, line_ids, context=context)
        else:
            need_reload = any(id == attachment.id for attachment in wizard.document_ids)
            line_ids = [attachment.id for attachment in wizard.document_ids]
            self.pool.get('change.directory.document').change_directory_button(cr, uid, line_ids, context=context)

            if need_reload:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'reload'
                }

        return {'type': 'ir.actions.act_window_close'}

class change_directory_document(osv.TransientModel):
    """
        A model to configure Directory ID in documents wizard
    """

    _name = 'change.directory.document'
    _description = 'Change Directory Wizard Document'
    _columns = {
        'wizard_id': fields.many2one('change.directory.wizard', string='Wizard', required=True),
        'document_id': fields.many2one('ir.attachment', string='Document', readonly=True),
        'directory_name': fields.many2one('document.directory','Directory'),
    }

    def change_directory_button(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            directory_id = line.directory_name.id or False
            document_id = line.document_id.id or False
            if document_id and isinstance(document_id, (int, long)):
                document_id = [document_id]
            if document_id and directory_id:
                self.pool.get('ir.attachment').write(cr,uid,document_id, {'parent_id': directory_id}, context=context)

    def change_moveall_directory_button(self, cr, uid, ids, context=None):
        directory_id = context.get('directory_id')
        for line in self.browse(cr, uid, ids, context=context):
            document_id = line.document_id.id or False
            if document_id and isinstance(document_id, (int, long)):
                document_id = [document_id]
            if document_id:
                self.pool.get('ir.attachment').write(cr,uid,document_id, {'parent_id': directory_id}, context=context)
