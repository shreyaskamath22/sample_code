from openerp.osv import fields, osv
from openerp.tools.translate import _
import base64
#from tools.translate import _
#from osv import osv, fields
import time
import datetime
import os
import logging
from lxml import etree
from openerp.osv.orm import setup_modifiers
import binascii
from base64 import b64decode
import xlsxwriter
from xlrd import open_workbook
import xlwt
import xlrd
from xlutils.copy import copy
import os.path
from openerp import api


_logger = logging.getLogger(__name__)

class wireless_link_type(osv.osv):
    _name='wireless.link.type'
    _columns={
        'name': fields.char('Links Type'),

}

wireless_link_type()


class wireless_maintenance_links(osv.osv):
    _name='wireless.maintenance.links'
    _columns={
        'name': fields.char('Links Name'),
        'wireless_links': fields.char('Link Url'),
        'link_type': fields.many2one('wireless.link.type','Link Type'),
        'link_id': fields.many2one('wireless.maintenance','Links'),
        'groups_access_links':fields.many2many('res.groups','links_res_group_rel','wireless_links_id','group_id','Associated Security Groups'),
        'department_access': fields.many2many('hr.department','departments_access_rel','department_id','hr_id','Associated Departments'),
        'comments': fields.text('Description'),

}

wireless_maintenance_links()

class wireless_maintenance(osv.osv):
                
                
    _name='wireless.maintenance'
    _columns={
        # 'emergency_support' : fields.char('Emergency Support',size=890),
        'links_line':fields.one2many('wireless.maintenance.links','link_id','Quick Links'),
        'name': fields.char('Name'),
        #'master_links_line': fields.function(_get_links,type="one2many",obj="wireless.maintenance.links",method=True,string="Quick Links",store=False),

}

    def default_get(self, cr, uid, fields, context=None):
        res = super(wireless_maintenance, self).default_get(cr, uid, fields, context=context)
        main_user_id = uid
        master_links_obj=self.pool.get('wireless.maintenance.links')
        maintenance_obj=self.pool.get('wireless.maintenance')
        line_data = []
        links_groups_users_ids = []
        search_master_links = master_links_obj.search(cr,uid,[])
        if search_master_links:
            for o in master_links_obj.browse(cr,uid,search_master_links):
                main_form_id = o.id
                cr.execute('select group_id from links_res_group_rel where wireless_links_id = %s',(main_form_id,))
                links_res_group_rel_ids = map(lambda x: x[0], cr.fetchall())
                if links_res_group_rel_ids==[]:
                    line_data.append({
                                'name':o.name,
                                'wireless_links':o.wireless_links,
                                'link_type': o.link_type.id,
                                'comments':o.comments
                    })
                #for links_res_group in links_res_group_rel_ids:
                if links_res_group_rel_ids:
                    cr.execute('select uid from res_groups_users_rel where gid in %s',(tuple(links_res_group_rel_ids),))
                    links_groups_users_ids = map(lambda x: x[0], cr.fetchall())
                    if (main_user_id in links_groups_users_ids):
                        line_data.append({
                                'name':o.name,
                                'wireless_links':o.wireless_links,
                                'link_type':o.link_type.id,
                                'comments': o.comments
                        })
                        print "line_data", line_data,o.wireless_links
            res.update({'links_line': line_data})
        return res
    

wireless_maintenance()


class export_table(osv.osv):
    _name = 'export.table'

    def _file_read(self, cr, uid, location, fname, bin_size=False):
        r = ''
        try:
                if bin_size:
                        r = os.path.getsize(location)
                else:
                        r = open(location,'rb').read().encode('base64')
        except IOError:
                _logger.error("_read_file reading %s",location)
        return r

    def _retrieve_file(self, cr, uid, ids, name, value, arg, context=None):
        if context is None:
                context = {}
        result = {}
        attach = self.browse(cr, uid, ids[0], context=context)        
        bin_size = context.get('bin_size')
        if attach.file_url:
                result[attach.id] = self._file_read(cr, uid, attach.file_url, attach.file_name, bin_size)
        else:
                result[attach.id] = value
        return result

    _columns = {
                'model_name':fields.many2one('ir.model','Model'),
                'fields_access':fields.many2many('ir.model.fields','fields_relation_rel','main_id','fields_id','Model Fields'),
                'export_file': fields.function(_retrieve_file, type='binary', string='File', nodrop=True, readonly=True),
                'file_url':fields.char('File URL'),
                'file_name':fields.char('File Name')
                }

    def export_data(self, cr, uid, ids, context=None):
        path_obj = self.pool.get('export.table.config')
        field_obj = self.pool.get('ir.model.fields')
        model_obj = self.pool.get('ir.model')
        self_data = self.browse(cr, uid, ids[0])
        path_ids = path_obj.search(cr, uid, [])
        directory = path_obj.browse(cr, uid, path_ids[0]).path
        main_id = self_data.id
        append_values = []
        column_values = str('')
        append_object_values = []
        model_id = self_data.model_name.id
        model_name = self_data.model_name.model
        table_name = model_name.replace('.','_')
        # ####### All Columns of table ##############
        # cr.execute("select column_name from information_schema.columns where table_name = '"+table_name+"';")
        # columns_unicode_values = map(lambda x: x[0], cr.fetchall())
        # columns_values = [str(x) for x in columns_unicode_values]
        # ##############
        # for columns_names_values in columns_values:
        #     ############ Columns Type Data #################
        #     cr.execute("select relation from ir_model_fields where model_id=%s and name = %s",(model_id,columns_names_values))
        #     object_names = map(lambda x: x[0], cr.fetchall())
        #     object_names_values = [str(a) for a in object_names]
        #     append_object_values.append(object_names_values[0])
        #     ############ Column Name Data #############
        #     cr.execute("select field_description from ir_model_fields where model_id=%s and name = %s",(model_id,columns_names_values))
        #     columns_names = map(lambda x: x[0], cr.fetchall())
        #     columns_names_values = [str(y) for y in columns_names]
        #     append_values.append(columns_names_values[0])
        ########## selected fields to export ##########
        fields_to_export = self_data.fields_access
        join_list = str('')
        count = 1
        for field_each in fields_to_export:
            append_values.append(field_each.field_description)
            if field_each.ttype == 'many2one':
                relation_obj = field_each.relation.replace('.','_')
                join_list += str(' inner join %s t%s ON (t%s.id = pos.%s) '%(relation_obj,count,count,field_each.name))
                rec_name = str(self.pool.get(field_each.relation)._rec_name)
                if not rec_name:
                    model_ids = model_obj.search(cr, uid, [('model','=',field_each.relation)])
                    field_ids = field_obj.search(cr, uid, [('model_id','=',model_ids[0]),('name','=','name')])
                    if field_ids:
                        rec_name = str('name')
                if not rec_name:
                    rec_name = str('id')
                column_values += str('t%s.%s,'%(count,rec_name))
                count += 1
            else:
                column_values += str('pos.%s,'%(field_each.name))
        if column_values:
            column_values = column_values[:-1]
        ################ Extracting Table Records $$$$$$$$$$$$$$$
        cr.execute('''select '''+column_values+''' from '''+table_name+''' pos
         '''+join_list+''' limit 300''')

        d = map(lambda x: x, cr.fetchall())
        ####### xlsx file create and write values in it ##########
        new_file = '%s_%s.xlsx'%(table_name,main_id)
        full_path = directory + '/' + new_file
        workbook = xlsxwriter.Workbook(full_path)
        worksheet = workbook.add_worksheet()
        row = -1
        col = 0
        for key in d:
            row += 1
            col = 0
            if row == 0:
                for key1 in append_values:
                    if col == 0:
                        worksheet.write(row, col,'External ID')
                        col += 1
                    worksheet.write(row, col,key1)
                    col += 1
                row += 1
                col = 0
            list_key = list(key)
            for key1 in list_key:
                if col == 0:
                    worksheet.write(row, col, '__export__.%s_%s'%(table_name,key1))
                    col += 1
                worksheet.write(row, col, key1)
                col += 1
        workbook.close()
        # full_path = directory + '/' + new_file
        self.write(cr, uid, ids, {'file_url':full_path,'file_name':new_file})
        return True

export_table()

class export_table_config(osv.osv):
    _name = 'export.table.config'
    _columns = {
                'path':fields.char('Export File Storage Path')
    }

    def create(self, cr, uid, vals, context=None):
        path = vals.get('path')
        if not os.path.exists(path):
            raise osv.except_osv(('Warning!!'),('Directory does not exist.'))
        self_ids = self.search(cr, uid, [])
        if len(self_ids) >= 1:
            raise osv.except_osv(('Warning!!'),('One active File Store Path is already there. Please edit in that record.'))
        res = super(export_table_config,self).create(cr, uid, vals, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        path = vals.get('path')
        if path and not os.path.exists(path):
            raise osv.except_osv(('Warning!!'),('Directory does not exist.'))
        res = super(export_table_config,self).write(cr, uid, ids, vals, context=context)
        return res

export_table_config()