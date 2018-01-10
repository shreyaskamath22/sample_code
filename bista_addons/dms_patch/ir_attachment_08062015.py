import logging
import os
from openerp import tools
from openerp.tools.translate import _
from openerp.osv import osv,fields
from openerp.tools.translate import _
from openerp.http import request

_logger = logging.getLogger(__name__)

class ir_attachment(osv.osv):
    _inherit = 'ir.attachment'

    _columns = {
        'admin_doc_access': fields.char('Admin Access', help="This Fields give the access of directory to admin also"), 
        're_groups_doc_rel':fields.many2many('res.groups','re_doc_res_group_rel','docid','gid',"Read Groups"),
        're_users_doc_rel':fields.many2many('res.users','re_doc_res_users_rel','docid','users_id',"Read users"),
        'un_groups_doc_rel':fields.many2many('res.groups','un_doc_res_group_rel','docid','gid',"Unlink Group"),
        'un_users_doc_rel':fields.many2many('res.users','un_doc_res_users_rel','docid','users_id',"Unlink Users"),
        'wr_groups_doc_rel':fields.many2many('res.groups','wr_doc_res_group_rel','docid','gid',"Write Group"),
        'wr_users_doc_rel':fields.many2many('res.users','wr_doc_res_users_rel','docid','users_id',"Write Users"),
        'attachment_url':fields.char('URL', readonly = "1", help="This is an URL of documents"),        
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

#        if isinstance(res, (int, long)):
#            res = [res]
	
        store_fname_value = self.browse(cr,uid,res).store_fname or False
	dms_config_ids = dms_config_obj.search(cr,uid,[('active','=',True)])
	if dms_config_ids:
	    directory_name = dms_config_obj.browse(cr,uid,dms_config_ids[0]).directory_name or ''
	    if not directory_name:
		raise osv.except_osv(_('Warning'),_("Check the DMS configuration. Directory is not set"))
	else:
	    raise osv.except_osv(_('Warning'),_("Check the DMS configuration"))
        host_url = request.httprequest.host_url

        link_url = str(host_url)+'base/static/img/'+str(directory_name) + str(store_fname_value)
        if link_url and res:
	    cr.execute("update ir_attachment set index_content = null,db_datas = null,attachment_url = %s where id = %s",(str(link_url),str(res)))
#            self.write(cr,uid,res,{'attachment_url':str(link_url)})
        #######Code written to put the project files into the Projet Folder###
#        active_model = context.get('active_model',False)
#        parent_id = context.get('parent_id',False)
#        if active_model == 'document.directory':
#            cr.execute('update ir_attachment set parent_id=%s where id =%s',(parent_id,res))
#        else:
#            document_directory_search = doc_dir_obj.search(cr,uid,[('model_id','=','project.project')]) 
#            if document_directory_search[0]:
#                cr.execute('update ir_attachment set parent_id=%s where id =%s',(document_directory_search[0],res))
        return res        

    def write(self, cr, uid, ids, vals, context=None):
        doc_dir_obj = self.pool.get('document.directory')
        res_groups_obj = self.pool.get('res.groups')
        res_users_obj = self.pool.get('res.users')
        hr_employee_obj = self.pool.get('hr.employee')
        dms_config_obj = self.pool.get('dms.config')

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
        link_url = str(host_url)+'base/static/img/'+str(directory_name) + str(store_fname_value)

#        link_url = str(host_url)+'base/static/img/dms_06012015/' + str(store_fname_value)
        if link_url and ids:
	    cr.execute("update ir_attachment set index_content = null,db_datas = null,attachment_url = %s  where id = %s",(str(link_url),str(ids[0])))
#            self.write(cr,uid,ids,{'attachment_url':str(link_url)})
	return res        

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
