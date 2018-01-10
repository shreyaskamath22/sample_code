import logging
from openerp.osv import osv, fields
from openerp import tools
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class document_directory(osv.osv):
    _inherit = 'document.directory'
    _columns = {
        'admin_access': fields.char('Admin Access', help="This Fields give the access of directory to admin also"),
        're_users_dir_rel':fields.many2many('res.users','re_dir_res_users_rel','dirid','users_id',"read users"),
    	'un_groups_dir_rel':fields.many2many('res.groups','un_dir_res_group_rel','dirid','gid',"unlink Group"),
    	'un_users_dir_rel':fields.many2many('res.users','un_dir_res_users_rel','dirid','users_id',"unlink users"),
    	'wr_groups_dir_rel':fields.many2many('res.groups','wr_dir_res_group_rel','dirid','gid',"write Group"),
    	'wr_users_dir_rel':fields.many2many('res.users','wr_dir_res_users_rel','dirid','users_id',"write users"),
    	'cr_groups_dir_rel':fields.many2many('res.groups','cr_dir_res_group_rel','dirid','gid',"create Group"),
    	'cr_users_dir_rel':fields.many2many('res.users','cr_dir_res_users_rel','dirid','users_id',"create users"),
        're_job_dir_rel':fields.many2many('hr.job','re_job_dir_rel','dirid','jobid',"Job Positions"),
        'cr_job_dir_rel':fields.many2many('hr.job','cr_job_dir_rel','dirid','jobid',"Job Positions"),
        'wr_job_dir_rel':fields.many2many('hr.job','wr_job_dir_rel','dirid','jobid',"Job Positions"),
        'un_job_dir_rel':fields.many2many('hr.job','un_job_dir_rel','dirid','jobid',"Job Positions"),
        ##added by shreyas
        'model_id': fields.many2one('ir.model','Model Name'),
        'dir_intranet_check':fields.boolean('Intranet'),
#        'publish_start_date':fields.date('Publish Start Date'),
#        'publish_end_date':fields.date('Publish End Date'),
    }
    _defaults = {
                'admin_access':1,
    }    

    def check_read(self,cr,uid,groups_dir_ids,users_dir_ids,re_users_dir_ids,re_groups_dir_ids):
        res_users_obj = self.pool.get('res.users')
        if users_dir_ids and re_users_dir_ids and list(set(users_dir_ids).intersection(re_users_dir_ids)):
            return True
        elif groups_dir_ids and re_groups_dir_ids and list(set(groups_dir_ids).intersection(re_groups_dir_ids)):
            return True
        elif users_dir_ids:
            for users_dir_id in users_dir_ids:
                cr.execute('select gid from res_groups_users_rel where uid = %s'%(users_dir_id))
                res_groups_users_ids = map(lambda x: x[0], cr.fetchall())

                if res_groups_users_ids and list(set(res_groups_users_ids).intersection(re_groups_dir_ids)):
                    return True
                else:
                    if users_dir_id:
                        username = res_users_obj.browse(cr,uid,[users_dir_id]).name
                        if username:
                            raise osv.except_osv(_('Access Denied!'), _('You are going to add such user - '+username+' which is not have read access of the file')) 
                        else: 
                            raise osv.except_osv(_('Access Denied!'), _('You are going to add such user (ID - '+users_dir_id+') which is not have read access of the file')) 
        else:
            raise osv.except_osv(_('Access Denied!'), _('You are going to add such user/groups which is not have read access'))

        return True 

    def create(self, cr, uid, vals, context=None):
    #####res is used in create. hence it's returned on top
        res = super(document_directory, self).create(cr, uid, vals, context=context) 

        if vals['cr_users_dir_rel'] and len(vals['cr_users_dir_rel']) == 1:
            cr_users_dir_values = vals.get('cr_users_dir_rel')[0]
            if len(cr_users_dir_values) == 3:
                cr_users_dir_ids = cr_users_dir_values[2]
            else:
                cr_users_dir_ids = False
        else:
            cr_users_dir_ids = False 
        
        if vals['cr_groups_dir_rel'] and len(vals['cr_groups_dir_rel']) == 1:
            cr_groups_dir_values = vals.get('cr_groups_dir_rel')[0]
            if len(cr_groups_dir_values) == 3:
                cr_groups_dir_ids = cr_groups_dir_values[2]
            else:
                cr_groups_dir_ids = False
        else:
            cr_groups_dir_ids = False         


        if vals['wr_users_dir_rel'] and len(vals['wr_users_dir_rel']) == 1:
            wr_users_dir_values = vals.get('wr_users_dir_rel')[0]
            if len(wr_users_dir_values) == 3:
                wr_users_dir_ids = wr_users_dir_values[2]
            else:
                wr_users_dir_ids = False
        else:
            wr_users_dir_ids = False 
        
        if vals['wr_groups_dir_rel'] and len(vals['wr_groups_dir_rel']) == 1:
            wr_groups_dir_values = vals.get('wr_groups_dir_rel')[0]
            if len(wr_groups_dir_values) == 3:
                wr_groups_dir_ids = wr_groups_dir_values[2]
            else:
                wr_groups_dir_ids = False
        else:
            wr_groups_dir_ids = False  


        if vals['un_users_dir_rel'] and len(vals['un_users_dir_rel']) == 1:
            un_users_dir_values = vals.get('un_users_dir_rel')[0]
            if len(un_users_dir_values) == 3:
                un_users_dir_ids = un_users_dir_values[2]
            else:
                un_users_dir_ids = False
        else:
            un_users_dir_ids = False 
        
        if vals['un_groups_dir_rel'] and len(vals['un_groups_dir_rel']) == 1:
            un_groups_dir_values = vals.get('un_groups_dir_rel')[0]
            if len(un_groups_dir_values) == 3:
                un_groups_dir_ids = un_groups_dir_values[2]
            else:
                un_groups_dir_ids = False
        else:
            un_groups_dir_ids = False  


        if vals['re_users_dir_rel'] and len(vals['re_users_dir_rel']) == 1:
            re_users_dir_values = vals.get('re_users_dir_rel')[0]
            if len(re_users_dir_values) == 3:
                re_users_dir_ids = re_users_dir_values[2]
            else:
                re_users_dir_ids = False
        else:
            re_users_dir_ids = False 
        if vals['group_ids'] and len(vals['group_ids']) == 1:
            re_groups_dir_values = vals.get('group_ids')[0]
            if len(re_groups_dir_values) == 3:
                re_groups_dir_ids = re_groups_dir_values[2]
            else:
                re_groups_dir_ids = False
        else:
            re_groups_dir_ids = False

        #####Job Position Start
        cr.execute('select jobid from re_job_dir_rel where dirid = %s'%(res))
        re_job_dir_ids = map(lambda x: x[0], cr.fetchall())
        cr.execute('select jobid from cr_job_dir_rel where dirid = %s'%(res))
        cr_job_dir_ids = map(lambda x: x[0], cr.fetchall())
        cr.execute('select jobid from wr_job_dir_rel where dirid = %s'%(res))
        wr_job_dir_ids = map(lambda x: x[0], cr.fetchall())
        cr.execute('select jobid from un_job_dir_rel where dirid = %s'%(res))
        un_job_dir_ids = map(lambda x: x[0], cr.fetchall())
        #####Job Position End

        if re_job_dir_ids and cr_job_dir_ids and len(list(set(cr_job_dir_ids).intersection(re_job_dir_ids))) != len(cr_job_dir_ids):
                raise osv.except_osv(_('Warning'),_("You have entered such Create Job Position in directory which don't have read access of this directory."))
        elif re_job_dir_ids and wr_job_dir_ids and len(list(set(wr_job_dir_ids).intersection(re_job_dir_ids))) != len(wr_job_dir_ids):
                raise osv.except_osv(_('Warning'),_("You have entered such Write Job Position in directory which don't have read access of this directory."))
        elif re_job_dir_ids and un_job_dir_ids and len(list(set(un_job_dir_ids).intersection(re_job_dir_ids))) != len(un_job_dir_ids):
                raise osv.except_osv(_('Warning'),_("You have entered such Delete Job Position in directory which don't have read access of this directory."))

        if (cr_users_dir_ids or cr_groups_dir_ids) and re_users_dir_ids == False and re_groups_dir_ids == False:
            raise osv.except_osv(_('Access Denied!'), _('Before assigning create access you must need to give read access of directory'))
        elif cr_users_dir_ids or cr_groups_dir_ids:
            self.check_read(cr,uid,cr_groups_dir_ids,cr_users_dir_ids,re_users_dir_ids,re_groups_dir_ids)

        if (wr_users_dir_ids or wr_groups_dir_ids) and re_users_dir_ids == False and re_groups_dir_ids == False:
            raise osv.except_osv(_('Access Denied!'), _('Before assigning write access you must need to give read access of directory'))
        elif wr_users_dir_ids or wr_groups_dir_ids:
            self.check_read(cr,uid,wr_groups_dir_ids,wr_users_dir_ids,re_users_dir_ids,re_groups_dir_ids)

        if un_users_dir_ids or un_groups_dir_ids and re_users_dir_ids == False and re_groups_dir_ids == False:
            raise osv.except_osv(_('Access Denied!'), _('Before assigning unlink access you must need to give read access of directory'))
        elif un_users_dir_ids or un_groups_dir_ids:
            self.check_read(cr,uid,un_groups_dir_ids,un_users_dir_ids,re_users_dir_ids,re_groups_dir_ids)                             
        return res        

    def write(self, cr, uid, ids, vals, context=None):
        res = super(document_directory, self).write(cr, uid, ids, vals, context=context)
        
        if 'cr_users_dir_rel' in vals:
            if len(vals.get('cr_users_dir_rel')) == 1:
                cr_users_dir_values = vals.get('cr_users_dir_rel')[0]
                if len(cr_users_dir_values) == 3:
                    cr_users_dir_ids = cr_users_dir_values[2]
                else:
                    cr_users_dir_ids = False
            else:
                cr_users_dir_ids = False
        else:
            cr_users_dir_ids = False

        if 'cr_groups_dir_rel' in vals:
            if len(vals.get('cr_groups_dir_rel')) == 1:
                cr_groups_dir_values = vals.get('cr_groups_dir_rel')[0]
                if len(cr_groups_dir_values) == 3:
                    cr_groups_dir_ids = cr_groups_dir_values[2]
                else:
                    cr_groups_dir_ids = False
            else:
                cr_groups_dir_ids = False
        else:
            cr_groups_dir_ids = False

        
        if 'wr_users_dir_rel' in vals:
            if len(vals.get('wr_users_dir_rel')) == 1:
                wr_users_dir_values = vals.get('wr_users_dir_rel')[0]
                if len(wr_users_dir_values) == 3:
                    wr_users_dir_ids = wr_users_dir_values[2]
                else:
                    wr_users_dir_ids = False
            else:
                wr_users_dir_ids = False
        else:
            wr_users_dir_ids = False

        if 'wr_groups_dir_rel' in vals:
            if len(vals.get('wr_groups_dir_rel')) == 1:
                wr_groups_dir_values = vals.get('wr_groups_dir_rel')[0]
                if len(wr_groups_dir_values) == 3:
                    wr_groups_dir_ids = wr_groups_dir_values[2]
                else:
                    wr_groups_dir_ids = False
            else:
                wr_groups_dir_ids = False
        else:
            wr_groups_dir_ids = False

        
        if 'un_users_dir_rel' in vals:
            if len(vals.get('un_users_dir_rel')) == 1:
                un_users_dir_values = vals.get('un_users_dir_rel')[0]
                if len(un_users_dir_values) == 3:
                    un_users_dir_ids = un_users_dir_values[2]
                else:
                    un_users_dir_ids = False
            else:
                un_users_dir_ids = False
        else:
            un_users_dir_ids = False

        if 'un_groups_dir_rel' in vals:
            if len(vals.get('un_groups_dir_rel')) == 1:
                un_groups_dir_values = vals.get('un_groups_dir_rel')[0]
                if len(un_groups_dir_values) == 3:
                    un_groups_dir_ids = un_groups_dir_values[2]
                else:
                    un_groups_dir_ids = False
            else:
                un_groups_dir_ids = False
        else:
            un_groups_dir_ids = False                

        cr.execute('select group_id from document_directory_group_rel where item_id = %s'%(ids[0]))
        re_groups_dir_ids = map(lambda x: x[0], cr.fetchall()) or False                         
        cr.execute('select users_id from re_dir_res_users_rel where dirid = %s'%(ids[0]))
        re_users_dir_ids = map(lambda x: x[0], cr.fetchall()) or False                     
        ####Start Job Position
        
        #####Job Position Start
        cr.execute('select jobid from re_job_dir_rel where dirid = %s'%(ids[0]))
        re_job_dir_ids = map(lambda x: x[0], cr.fetchall())
        cr.execute('select jobid from cr_job_dir_rel where dirid = %s'%(ids[0]))
        cr_job_dir_ids = map(lambda x: x[0], cr.fetchall())
        cr.execute('select jobid from wr_job_dir_rel where dirid = %s'%(ids[0]))
        wr_job_dir_ids = map(lambda x: x[0], cr.fetchall())
        cr.execute('select jobid from un_job_dir_rel where dirid = %s'%(ids[0]))
        un_job_dir_ids = map(lambda x: x[0], cr.fetchall())
        #####Job Position End
                       
        if re_job_dir_ids and cr_job_dir_ids and len(list(set(cr_job_dir_ids).intersection(re_job_dir_ids))) != len(cr_job_dir_ids):
                raise osv.except_osv(_('Warning'),_("You have entered such Create Job Position in directory which don't have read access of this directory."))
        elif re_job_dir_ids and wr_job_dir_ids and len(list(set(wr_job_dir_ids).intersection(re_job_dir_ids))) != len(wr_job_dir_ids):
                raise osv.except_osv(_('Warning'),_("You have entered such Write Job Position in directory which don't have read access of this directory."))
        elif re_job_dir_ids and un_job_dir_ids and len(list(set(un_job_dir_ids).intersection(re_job_dir_ids))) != len(un_job_dir_ids):
                raise osv.except_osv(_('Warning'),_("You have entered such Delete Job Position in directory which don't have read access of this directory."))

        ####End Job Position

        if (cr_users_dir_ids or cr_groups_dir_ids) and re_users_dir_ids == False and re_groups_dir_ids == False:
            raise osv.except_osv(_('Access Denied!'), _('Before assigning create access you must need to give read access of directory'))
        elif cr_users_dir_ids or cr_groups_dir_ids:
            self.check_read(cr,uid,cr_groups_dir_ids,cr_users_dir_ids,re_users_dir_ids,re_groups_dir_ids)

        if (wr_users_dir_ids or wr_groups_dir_ids) and not re_users_dir_ids == False and re_groups_dir_ids == False:
            raise osv.except_osv(_('Access Denied!'), _('Before assigning write access you must need to give read access of directory'))
        elif wr_users_dir_ids or wr_groups_dir_ids:
            self.check_read(cr,uid,wr_groups_dir_ids,wr_users_dir_ids,re_users_dir_ids,re_groups_dir_ids)

        if (un_users_dir_ids or un_groups_dir_ids) and re_users_dir_ids == False and re_groups_dir_ids == False:
            raise osv.except_osv(_('Access Denied!'), _('Before assigning unlink access you must need to give read access of directory'))
        elif un_users_dir_ids or un_groups_dir_ids:
            self.check_read(cr,uid,un_groups_dir_ids,un_users_dir_ids,re_users_dir_ids,re_groups_dir_ids)        

        return res 
document_directory()
