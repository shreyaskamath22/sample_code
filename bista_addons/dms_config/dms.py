from openerp.osv import fields, osv
import logging

logger = logging.getLogger('arena_log')

class dms_config(osv.osv):
    _name = "dms.config"
    _description = "DMS Configuration"
    _columns = {
        'directory_name': fields.char('Directory', help="Enter directory name here"),
        'file_path': fields.char('File Path', help="Enter file path here"),
        'active':fields.boolean('Active',help="If it's active then this path will use for configuration"),
        'attachment_path': fields.char('Attachment Link File Path', help="Enter Merge File Path over here"),
    }

    def create(self, cr, uid, vals, context=None):
        res = super(dms_config, self).create(cr, uid, vals, context=context)
        active = vals.get('active',False)
        if active:
            active_ids = self.search(cr, uid, [('active','=',True),('id','!=',res)])
            logger.info("context------%s-------------res-------%s---------%s"%(active,res,active_ids))
            if active_ids and len(active_ids) > 1:
                raise osv.except_osv(('Warning'),("You can not make two path active at one time. First go and make inactive to the active path or else contact your admin. It's might be lost your system integration."))
        return res  

    def write(self, cr, uid, ids, vals, context=None):
        res = super(dms_config, self).write(cr, uid, ids, vals, context=context)
        if 'active' in vals:
            active = vals.get('active',False)
        else:
            active = self.browse(cr,uid,ids).active or False
        if active:
            active_ids = self.search(cr, uid, [('active','=',True),('id','!=',ids[0])])
            if active_ids and len(active_ids) > 1:
                raise osv.except_osv(('Warning'),("You can not make two path active at one time. First go and make inactive to the active path or else contact your admin. It's might be lost your system integration."))
        return res


#    def default_get(self, cr, uid, fields, context=None):
#        res = super(dms_config, self).default_get(cr, uid, fields, context=context)
#        cr.execute('select id from dms_config')
#        data = map(lambda x: x[0], cr.fetchall())
#        if data:
#            obj = self.browse(cr, uid, data, context)
#            res['directory_name'] = obj.directory_name
#            res['file_path'] = obj.file_path
#        return res

    def save(self, cr, uid, ids, context=None):
        return True

dms_config()
