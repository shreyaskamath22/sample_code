import hashlib
import itertools
import logging
import os
import re
import time

from openerp import tools
from openerp.tools.translate import _
from openerp.exceptions import AccessError
from openerp.osv import fields,osv
from openerp import SUPERUSER_ID

from openerp.http import request, serialize_exception as _serialize_exception

_logger = logging.getLogger(__name__)


class ir_attachment_log(osv.osv):
    _name = 'ir.attachment.log'
    _columns = {
        'name':fields.char('File Name', readonly=True), 
        'user_id':fields.many2one('res.users','User', readonly=True),
        'write_date':fields.datetime('Modification', readonly=True),
        'status':fields.selection([('arch','Archived'),('cur','Active')],'Status', readonly=True),
        'old_file':fields.binary('Upload', readonly=True),
        'ir_log_id':fields.many2one('ir.attachment','Attachment'),
    }    

    _defaults = {
        "write_date": lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": 'arch',

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
        fname_to_delete = attach.store_fname
        if location != 'db':
            fname = self._file_write(cr, uid, id, value)
            # SUPERUSER_ID as probably don't have write access, trigger during create
            super(ir_attachment, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size, 'db_datas': False}, context=context)
        else:
            super(ir_attachment, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size, 'store_fname': False}, context=context)

        # After de-referencing the file in the database, check whether we need
        # to garbage-collect it on the filesystem
        if fname_to_delete:
            self._file_delete(cr, uid, fname_to_delete)
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
        'un_groups_doc_rel':fields.many2many('res.groups','un_doc_res_group_rel','docid','gid',"Unlink Group"),
        'un_users_doc_rel':fields.many2many('res.users','un_doc_res_users_rel','docid','users_id',"Unlink Users"),
        'wr_groups_doc_rel':fields.many2many('res.groups','wr_doc_res_group_rel','docid','gid',"Write Group"),
        'wr_users_doc_rel':fields.many2many('res.users','wr_doc_res_users_rel','docid','users_id',"Write Users"),
        "log_ids": fields.one2many('ir.attachment.log', 'ir_log_id', 'Log lines'),
        'attachment_url':fields.char('URL', help="This is an URL of documents"), 
        # 'cr_url':fields.function(_get_url, type='char', string='Url'),
        # 'has_logs': fields.function(_has_logs, type="boolean"),
        
    }
    _defaults = {
                'admin_doc_access':1,
    } 


#####Inherit create      
    def create(self, cr, uid, vals, context=None):

        doc_dir_obj = self.pool.get('document.directory')
        res_groups_obj = self.pool.get('res.groups')
        res_users_obj = self.pool.get('res.users')
        hr_employee_obj = self.pool.get('hr.employee')
        dms_config_obj = self.pool.get('dms.config')

        directory_name = ''        

        if context and uid != 1:
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
                    #####Checked the users access rights
                        if not cr_dir_res_group_ids and not cr_dir_res_users_ids:
                            pass
                        elif cr_dir_res_users_ids and uid in cr_dir_res_users_ids:
                        #####If found match it'll allow to create documents
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
                                raise osv.except_osv(_('Access Denied!'), _('You are not allowed to create this record. \nKindly check configuration or contact to your administrator'))
                        else:
                            raise osv.except_osv(_('Access Denied!'), _('You are not allowed to create this record. \nKindly check configuration or contact to your administrator'))
        res = super(ir_attachment, self).create(cr, uid, vals, context=context)
        if isinstance(res, (int, long)):
            res = [res]

        store_fname_value = self.browse(cr,uid,res).store_fname or False
        host_url = request.httprequest.host_url
        dms_config_ids = dms_config_obj.search(cr,uid,[('active','=',True)])

        if dms_config_ids:
            directory_name = dms_config_obj.browse(cr,uid,dms_config_ids[0]).directory_name or ''
            if not directory_name:
                raise osv.except_osv(_('Warning'),_("Check the DMS configuration. Directory is not set"))
        else:
            raise osv.except_osv(_('Warning'),_("Check the DMS configuration")) 

        link_url = 'base/static/img/'+str(directory_name) + str(store_fname_value)
        link_url = link_url.replace("//", "/");
        link_url = str(host_url)+str(link_url)
        if link_url and res:
            cr.execute("update ir_attachment set index_content = null,db_datas = null,attachment_url = %s where id in %s",(str(link_url),tuple(res)))
            # self.write(cr,uid,res,{'attachment_url':str(link_url)})
        return res        

    def write(self, cr, uid, ids, vals, context=None):
        doc_dir_obj = self.pool.get('document.directory')
        res_groups_obj = self.pool.get('res.groups')
        res_users_obj = self.pool.get('res.users')
        hr_employee_obj = self.pool.get('hr.employee')
        dms_config_obj = self.pool.get('dms.config')

        directory_name = ''        

        if context and uid != 1:
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
                        if not wr_dir_res_users_ids and not wr_dir_res_group_ids:
                            pass
                        elif wr_dir_res_users_ids and uid in wr_dir_res_users_ids:
                        #####If found match it'll allow to edit documents                            
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
                                    raise osv.except_osv(_('Access Denied!'), _('You are not allowed to edit this record. \nKindly check configuration or contact to your administrator'))
                        else:
                            raise osv.except_osv(_('Access Denied!'), _('You are not allowed to edit this record. \nKindly check configuration or contact to your administrator'))
 
        res = super(ir_attachment, self).write(cr, uid, ids, vals, context=context)

        if isinstance(ids, (int, long)):
            ids = [ids]

        store_fname_value = self.browse(cr,uid,ids).store_fname or False
        host_url = request.httprequest.host_url
        dms_config_ids = dms_config_obj.search(cr,uid,[('active','=',True)])

        if dms_config_ids:
            directory_name = dms_config_obj.browse(cr,uid,dms_config_ids[0]).directory_name or ''
            if not directory_name:
                raise osv.except_osv(_('Warning'),_("Check the DMS configuration. Directory is not set"))
        else:
            raise osv.except_osv(_('Warning'),_("Check the DMS configuration"))        
        link_url = 'base/static/img/'+str(directory_name) + str(store_fname_value)
        link_url = link_url.replace("//", "/");
        link_url = str(host_url)+str(link_url)
        if link_url and ids:
            cr.execute("update ir_attachment set index_content = null,db_datas = null,attachment_url = %s  where id = %s",(str(link_url),str(ids[0])))
#            self.write(cr,uid,ids,{'attachment_url':str(link_url)})
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
                    #####Checked the users access rights
                        if not un_dir_res_group_ids and not un_dir_res_users_ids:
                            raise osv.except_osv(_('Access Denied!'), _('You are not allowed to delete this record. \nKindly check configuration or contact to your administrator'))
                            # pass
                        elif un_dir_res_users_ids and uid in un_dir_res_users_ids:
                        #####If found match it'll allow to delete documents                            
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
                                    raise osv.except_osv(_('Access Denied!'), _('You are not allowed to delete this record. \nKindly check configuration or contact to your administrator'))
                        else:
                            raise osv.except_osv(_('Access Denied!'), _('You are not allowed to delete this record. \nKindly check configuration or contact to your administrator'))

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
        	path = path.replace("//", "/");

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

#    def _file_read(self, cr, uid, fname, bin_size=False):
#        full_path = self._full_path(cr, uid, fname)
#        r = ''
#        try:
#            if bin_size:
#                if os.path.exists(full_path):
#                r = os.path.getsize(full_path)
#                else:
#                    raise osv.except_osv(_('Warning!'), _('File Path is Not exist, Kindly contact to your admin'))
#            else:
#                r = open(full_path,'rb').read().encode('base64')
#        except IOError:
#            _logger.exception("_read_file reading %s", full_path)

#        r = super(ir_attachment, self)._file_read(self, cr, uid, fname, bin_size=False)
#        return r





ir_attachment()
