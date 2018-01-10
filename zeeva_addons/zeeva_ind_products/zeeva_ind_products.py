# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from osv import fields,osv
import tools
import pooler
import time
from tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import timedelta,date,datetime

from datetime import datetime,date
from openerp import netsvc

from openerp.tools.amount_to_text_en import amount_to_text
from openerp.tools import float_compare, float_round, DEFAULT_SERVER_DATETIME_FORMAT

import io
import cStringIO as StringIO
#import StringIO
import httplib

from PIL import Image
from PIL import ImageOps
from random import random

import math
import re
import os

import calendar
import xlsxwriter
import logging
import binascii
import base64
from base64 import b64decode
from xlrd import open_workbook
from openerp import SUPERUSER_ID


_logger = logging.getLogger(__name__)


#---------------------------------------------------------------------
# Created an Seperate Interface for the Product Customer Sale Price
#---------------------------------------------------------------------

# class product_customer(osv.osv):
#     _name = 'product.customer'
#     _description = 'Product Sale Price'
#     _columns = {
#         'product_id': fields.many2one('product.product','Products'),
#         'customer_saleprice': fields.one2many('product.customer.saleprice','customer_saleprice_id','Customer Sale Price'),
#     }

#     def read(self, cr, uid, ids, fields_to_read=None, context=None, load='_classic_read'):
#         if isinstance(ids, (int, long)):
#             ids = [ids]
#         res = super(product_customer, self).read(cr, uid, ids, fields_to_read, context, load)
#         return res

# product_customer()

class product_customer_saleprice(osv.osv):
    _name = 'product.customer.saleprice'
    _description = 'Customer Sale Price'
    _rec_name = 'sales_price'
    _columns = {
        #'customer_saleprice_id': fields.many2one('product.customer','Products One two many id'),
        'product_id': fields.many2one('product.product', 'Products'),
        'customer_id': fields.many2one('res.partner','Customer'),
        'sales_price': fields.float('Sale Price'),
    }
product_customer_saleprice()


class combo_product_line(osv.osv):
    _name = 'combo.product.line'
    _description = 'Combo Products'
    _columns = {
        'combo_product_id': fields.many2one('product.product','Combo Products'),
        'product_id': fields.many2one('product.product','Products'),
        'shipped_quantity':fields.float('Shipped Quantity'),
        'billed_quantity': fields.float('Billed Quantity'),
    }
combo_product_line()


class product_analysis(osv.osv):
    _name = 'product.analysis'
    _description = 'Product Analysis'

    #-------------------------------------------------------------------------------------------------------------
    #Created an Master for the searching as same as the History tab in Products Form and for the Reporting purpose
    #-------------------------------------------------------------------------------------------------------------

    def _get_so_lines(self, cr, uid, ids, append_values, field_names=None, arg=None):
            result = {}
            sale_order_obj = self.pool.get('sale.order')
            product_id = append_values[0]
            customer_id = append_values[1]
            from_date = append_values[2]
            to_date = append_values[3]
            if isinstance(customer_id,int):
                sale_order_search =sale_order_obj.search(cr,uid,[('partner_id','=',customer_id),('date_order','>=',from_date),('date_order','<=',to_date)])
                solines_pool = self.pool.get('sale.order.line')
                result[id] = solines_pool.search(cr, uid, [('product_id','=',product_id),('order_id','in',sale_order_search),('state','!=','cancel')])
            elif isinstance(customer_id,str):
                current_values = self.browse(cr,uid,ids[0])
                main_id =current_values.id
                product_id = current_values.product_id.id
                customer_id = current_values.customer_id.id
                from_date = current_values.from_date
                to_date = current_values.to_date
                sale_order_search =sale_order_obj.search(cr,uid,[('partner_id','=',customer_id),('date_order','>=',from_date),('date_order','<=',to_date)])
                solines_pool = self.pool.get('sale.order.line')
                result[main_id] = solines_pool.search(cr, uid, [('product_id', '=', product_id),('order_id','in',sale_order_search),('state','!=','cancel')])
            return result


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
        'product_id': fields.many2one('product.template','Product'),
        'customer_id': fields.many2one('res.partner','Customer'),
        'from_date': fields.date('From Date'),
        'to_date': fields.date('To Date'),
        'saleorderline_ids': fields.function(_get_so_lines, method=True,type='one2many', relation='sale.order.line', string='Sales Order Lines'),
        'export_file': fields.function(_retrieve_file, type='binary', string='File', nodrop=True, readonly=True),
        'file_url':fields.char('File URL'),
        'file_name':fields.char('File Name'),
        'file_upload': fields.binary('Upload a file'),
    }


    #-------------------------------------------------------
    #Export the data into the excel file through the button 
    #-------------------------------------------------------
    def export_data(self,cr,uid,ids,context):
        append_values=[]
        column_values = str('')
        column_values_line = str('')
        append_object_values = []
        append_one2many_values = []
        append_line_header =[]
        main_header = []
        line_header = ['create_date','product_uom_qty','order_id','order_partner_id','price_unit','state']
        main_id = ids[0]
        path_obj = self.pool.get('export.table.config')
        path_ids = path_obj.search(cr, uid, [])
        directory = path_obj.browse(cr, uid, path_ids[0]).path
        ir_model_obj = self.pool.get('ir.model')
        ir_model_fields_obj = self.pool.get('ir.model.fields')
        sale_order_obj = self.pool.get('sale.order')
        solines_pool = self.pool.get('sale.order.line')
        table_obj = self._name
        table_name = table_obj.replace('.','_')
        model_id = ir_model_obj.search(cr,uid,[('model','=',table_obj)])
        fields_id = ir_model_fields_obj.search(cr,uid,[('model_id','=',model_id[0])])
        join_list = str('')
        count = 1
        for field_each in ir_model_fields_obj.browse(cr,uid,fields_id):
            if field_each.ttype != 'one2many' and field_each.ttype != 'binary' and field_each.ttype != 'char':
                append_values.append(field_each.field_description)
                if field_each.ttype == 'many2one':
                    relation_obj = field_each.relation.replace('.','_')
                    join_list += str(' inner join %s t%s ON (t%s.id = pos.%s) '%(relation_obj,count,count,field_each.name))
                    rec_name = str(self.pool.get(field_each.relation)._rec_name)
                    if not rec_name:
                        model_ids = ir_model_obj.search(cr, uid, [('model','=',field_each.relation)])
                        field_ids = ir_model_fields_obj.search(cr, uid, [('model_id','=',model_ids[0]),('name','=','name')])
                        if field_ids:
                            rec_name = str('name')
                    if not rec_name:
                        rec_name = str('id')
                    column_values += str('t%s.%s,'%(count,rec_name))
                    count += 1
                elif field_each.ttype == 'date':
                    column_values += str('pos.%s,'%(field_each.name))
        if column_values:
            column_values = column_values[:-1]
        ################ Extracting Table Records $$$$$$$$$$$$$$$
        cr.execute('''select '''+column_values+''' from '''+table_name+''' pos
         '''+join_list)

        d = map(lambda x: x, cr.fetchall())
        ####### xlsx file create and write values in it ##########
        new_file = '%s_%s.xlsx'%(table_name,main_id)
        full_path = directory+'/'+new_file
        directory_path = directory
        workbook = xlsxwriter.Workbook(full_path)
        format1 = workbook.add_format({'bold': True, 'font_color': 'red'})
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
                        worksheet.set_row(0,18,format1)
                        col += 1
                    worksheet.write(row, col,key1)
                    col += 1
                row += 1
                col = 0
            list_key = list(key)
            for key1 in list_key:
                if col == 0:
                    worksheet.write(row, col, '__export__.%s_%s'%(table_name,main_id))
                    col += 1
                worksheet.write(row, col, key1)
                col += 1
        ################################# Sale Order Lines########
        saleorderlines_model_id = ir_model_obj.search(cr,uid,[('model','=','sale.order.line')])
        line_fields_id = ir_model_fields_obj.search(cr,uid,[('model_id','=',saleorderlines_model_id[0])])
        cr.execute('select name from ir_model_fields where id in %s',(tuple(line_fields_id),))
        name_values = map(lambda x: x[0], cr.fetchall())
        for name_values_id in name_values:
            if name_values_id in  line_header:
                append_line_header.append(name_values_id)
                cr.execute('select field_description from ir_model_fields where name in %s and model_id=%s',(tuple(append_line_header),saleorderlines_model_id[0]))
                field_description_name = map(lambda x: x[0], cr.fetchall())
        for field_each1 in ir_model_fields_obj.browse(cr,uid,fields_id):
            if field_each1.ttype == 'one2many':
                count = 1
                append_one2many_values.append(field_each1.field_description)
                o=self.browse(cr,uid,ids[0])
                product_id =o.product_id.id
                customer_id = o.customer_id.id
                from_date = o.from_date
                to_date = o.to_date
                sale_order_search =sale_order_obj.search(cr,uid,[('partner_id','=',customer_id),('date_order','>=',from_date),('date_order','<=',to_date)])
                lines_ids = solines_pool.search(cr, uid, [('product_id','=',product_id),('order_id','in',sale_order_search),('state','!=','cancel')])
                for lines_values in solines_pool.browse(cr,uid,lines_ids):
                    order_id = lines_values.order_id.name
                    order_date = lines_values.create_date
                    partner_id = lines_values.order_partner_id.name
                    product_uom_qty =lines_values.product_uom_qty
                    price_unit = lines_values.price_unit
                    state = lines_values.state
                    column_values_line += str('%s,%s,%s,%s,%s,%s;'%(order_date,order_id,price_unit,product_uom_qty,state,partner_id))
                    count += 1
        if column_values_line:
            column_values_line = column_values_line[:-1]
        column_values_line_list = column_values_line.split(';')
        row = 4
        col = 0
        for key3 in column_values_line_list:
            if row == 4:
                for main_header in append_one2many_values:
                    if col ==0:
                        worksheet.write(row, col,main_header)
                        worksheet.set_row(4,18,format1)
                        worksheet.set_row(5,18,format1)
            row += 1
            col = 0
            if row == 5:
                for key5 in field_description_name:
                    worksheet.write(row, col,key5)
                    col += 1
                row += 1
                col = 0
            list_key = list(key3)
            key_values = key3.split(',')
            for key4 in key_values:
                worksheet.write(row, col, key4)
                col += 1
        workbook.close()
        self.write(cr, uid, ids, {'file_url':full_path,'file_name':new_file})
        value_record = self._retrieve_file(cr, uid, ids, name='export_file',value=None,arg=None,context=None)
        return True


    #-------------------------------------------------------------------------
    #Writen an onchange for Filtering into the History tab in the Product Form
    #-------------------------------------------------------------------------
    def onchange_from_date(self,cr,uid,ids,product_id,customer_id,from_date,to_date):
        result={}
        append_values = [product_id,customer_id,from_date,to_date]
        if from_date and to_date:
            if from_date > to_date:
                raise osv.except_osv(('Warning!!'),('From Date Must Be Greater than To Date.'))
        val = self._get_so_lines(cr, uid, ids, append_values, field_names=None, arg=None)
        if val:
            for x,y in val.iteritems():
                if y:
                    for o in y:
                        v={'saleorderline_ids' : y}
                        result = {'value': v}
                        function_retrive= self.export_data(cr,uid,ids,context=None)
                        return result
                else:
                    v={'saleorderline_ids' : ''}
                    result = {'value': v}
                    return result

product_analysis()

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

#---------------------------------------------------------------------
# Created an Seperate Tab and Table for the Images in the Product Form
#---------------------------------------------------------------------

def image_resize_image(base64_source, size=(800, 800), encoding='base64', filetype='PNG', avoid_if_small=False):
        if not base64_source:
            return False
        if size == (None, None):
            return base64_source
        image_stream = io.BytesIO(base64_source.decode(encoding))
        image = Image.open(image_stream)

        asked_width, asked_height = size

        # check image size: do not create a thumbnail if avoiding smaller images
        if avoid_if_small and image.size[0] <= size[0] and image.size[1] <= size[1]:
            return base64_source

        if image.size <> size:
            
            # Save large image zeemage with a fixed width of 800px
            if asked_width == 800:
                if image.size[0] <= asked_width:
                    return base64_source
                    
                else:
                    temp_width = 800
                    temp_height = int(temp_width * image.size[1] / image.size[0])
                    size = temp_width, temp_height
                    
            # Save a medium image zeemage with a fixed height of 128px
            elif asked_height == 128:
                temp_height = 128
                temp_width = int(temp_height * image.size[0] / image.size[1])
                size = temp_width, temp_height
                
            # Save a product spec image with a fixed size 90px*70px
            elif asked_height == 70:
                size = 140, 140
            
            # Save a product thumbnail image with a fixed width of 64px
            elif asked_width == 64:
                temp_width = 64
                temp_height = int(temp_width * image.size[1] / image.size[0])
                size = temp_width, temp_height
            
            # Return a product image with a fixed width of 170px
            elif asked_width == 170:
                temp_width = 170
                temp_height = int(temp_width * image.size[1] / image.size[0])
                size = temp_width, temp_height
                
            else:
                return base64_source
            
            # If you need faster thumbnails you may use use Image.NEAREST
            image = ImageOps.fit(image, size, Image.ANTIALIAS)
        if image.mode not in ["1", "L", "P", "RGB", "RGBA"]:
            image = image.convert("RGB")

        background_stream = StringIO.StringIO()
        image.save(background_stream, filetype)
        return background_stream.getvalue().encode(encoding)

def image_resize_zeemage_large(base64_source, size=(800, None), encoding='base64', filetype='PNG', avoid_if_small=True):
        return image_resize_image(base64_source, size, encoding, filetype, avoid_if_small)

def image_resize_zeemage_medium(base64_source, size=(None, 128), encoding='base64', filetype='PNG', avoid_if_small=True):
        return image_resize_image(base64_source, size, encoding, filetype, avoid_if_small)

def image_resize_prod_spec(base64_source, size=(70, 70), encoding='base64', filetype='PNG', avoid_if_small=True):
        return image_resize_image(base64_source, size, encoding, filetype, avoid_if_small)

def image_resize_prod_thumbnail(base64_source, size=(64, None), encoding='base64', filetype='PNG', avoid_if_small=True):
        return image_resize_image(base64_source, size, encoding, filetype, avoid_if_small)

class product_image(osv.osv):

     # Read image
    def _get_image_large(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = {'image_large': obj.image}
        return result

     # Save 800px image and 128px image 
    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': image_resize_zeemage_large(value), 'image_medium': image_resize_zeemage_medium(value)}, context=context)

    _name = 'product.image'
    _description = 'Product Images'
    _columns = {
        'name': fields.char('Name', size=128),
        'product_image_id': fields.many2one('product.product','Product Images'),
        'image': fields.binary("Image", help="Large-size image with a width of 800px max"),
        'image_medium': fields.binary("Thumbnail", help="Medium-size image with a height of 128px max"),
        'image_large': fields.function(_get_image_large, fnct_inv=_set_image,
            string="Large-size image", type="binary", multi="_get_image_large",
            help="Large-size image with a width of 800px max"),
        'color': fields.integer('Color Index'),

    }

    _defaults = {
        'color': 0,
        'image': False,
    }

    def make_thumbnail(self, cr, uid, ids, context=None):
        
        for obj in self.browse(cr, uid, ids, context=context):
            
            if obj.product_image_id:  # it is a finished product
                obj.product_image_id.write({'image_medium': image_resize_prod_spec(obj.image), 
                                              'image_small': image_resize_prod_thumbnail(obj.image)}, context=context)

product_image()


class product_brand(osv.osv):

    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _name = "product.brand"
    _description = "Product Brands"
    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True, select=True),
        'parent_id': fields.many2one('product.brand','Parent Brand', select=True, ondelete='cascade'),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Name'),
        'type': fields.selection([('view','View'), ('normal','Normal')], 'Brand Type'),
        'active': fields.boolean('Active'),
    }

    _defaults={
            'type': 'normal',
            'active':True,
    }

product_brand()



#-----------------------------------------------------------------
# Inherit Default Products Module for Adding the additional Fields
#-----------------------------------------------------------------
def ean_checksum(eancode):
    """returns the checksum of an ean string of length 13, returns -1 if the string has the wrong length"""
    if len(eancode) <> 13:
        return -1
    oddsum=0
    evensum=0
    total=0
    eanvalue=eancode
    reversevalue = eanvalue[::-1]
    finalean=reversevalue[1:]

    for i in range(len(finalean)):
        if i % 2 == 0:
            oddsum += int(finalean[i])
        else:
            evensum += int(finalean[i])
    total=(oddsum * 3) + evensum

    check = int(10 - math.ceil(total % 10.0)) %10
    return check


def check_ean(eancode):
    """returns True if eancode is a valid ean13 string, or null"""
    if not eancode:
        return True
    if len(eancode) <> 13:
        return False
    try:
        int(eancode)
    except:
        return False
    return ean_checksum(eancode) == int(eancode[-1])

class product_template(osv.osv):
    _name = 'product.template'
    _inherit = ['product.template','mail.thread']
    _columns = {
        'state': fields.selection([('draft', 'Draft'),('submit_to_management','Submitted to Management'),('sellable','Approved')], 'State'),
    }

    _defaults={
            'state':'draft',
    }

product_template()

class product_product(osv.osv):
    _inherit = 'product.product'

    def _compute_cbm(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for p in self.browse(cr, uid, ids, context=context):
            if name == 'unit_cbm':
                res[p.id] = p.unit_l * p.unit_w * p.unit_h / 1000000
            elif name == 'pack_cbm':
                res[p.id] = p.pack_l * p.pack_w * p.pack_h / 1000000
            elif name == 'inner_cbm':
                res[p.id] = p.inner_l * p.inner_w * p.inner_h / 1000000
            elif name == 'export_cbm':
                res[p.id] = p.export_l * p.export_w * p.export_h / 1000000
            else: res[p.id] = 0
        return res

    def _no_of_pieces(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        for order in self.browse(cr, uid, ids):
            res[order.id] = {
                 'total_pieces': 0.0,
            }
            val = val1 = 0.0
            for line in order.combo_productline_id:
                val1 += line.shipped_quantity
            res[order.id] = val1
        return res

    def _compute_cuft(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for p in self.browse(cr, uid, ids, context=context):
            if name == 'unit_cuft':
                res[p.id] = p.unit_l * p.unit_w * p.unit_h * 35.315 / 1000000
            elif name == 'pack_cuft':
                res[p.id] = p.pack_l * p.pack_w * p.pack_h * 35.315 / 1000000
            elif name == 'inner_cuft':
                res[p.id] = p.inner_l * p.inner_w * p.inner_h * 35.315 / 1000000
            elif name == 'export_cuft':
                res[p.id] = p.export_l * p.export_w * p.export_h * 35.315 / 1000000
            else: res[p.id] = 0
        return res

#---------------------------------------------------------------
#Function inherited to Display the MRP Price in the Kanban view 
#---------------------------------------------------------------
    def _product_lst_price(self, cr, uid, ids, name, arg, context=None):
        res = {}
        product_uom_obj = self.pool.get('product.uom')
        for id in ids:
            res.setdefault(id, 0.0)
        for product in self.browse(cr, uid, ids, context=context):
            if 'uom' in context:
                uom = product.uos_id or product.uom_id
                res[product.id] = product_uom_obj._compute_price(cr, uid,
                        uom.id, product.list_price, context['uom'])
            else:
                res[product.id] = product.product_mrp
            res[product.id] =  (res[product.id] or 0.0) * (product.price_margin or 1.0) + product.price_extra
        return res

    def _product_check_permission(self, cr, uid, ids, name, arg, context=None):
        res={}
        res_groups_obj = self.pool.get('res.groups')
        groups_id_search = res_groups_obj.search(cr,uid,[('name','=','Products Manager')])
        search_id = groups_id_search[0]
        cr.execute('select uid from res_groups_users_rel where gid=%s',(search_id,))
        groups_user_id = map(lambda x: x[0], cr.fetchall())
        o =self.browse(cr,uid,ids[0])
        state = o.state
        user_id = uid
        if user_id in groups_user_id and state=='submit_to_management':
            res[o.id] = True
        else:
            res[o.id] = False
        return res

    def _get_so_lines(self, cr, uid, ids, customer_id, from_date, to_date, field_names=None, arg=None, context=None):
        result = {}
        if ids:
            sale_order_obj = self.pool.get('sale.order')
            if isinstance(customer_id,int):
                sale_order_search =sale_order_obj.search(cr,uid,[('partner_id','=',customer_id),('date_order','>=',from_date),('date_order','<=',to_date)])
                for id in ids:
                    solines_pool = self.pool.get('sale.order.line')
                    result[id] = solines_pool.search(cr, uid, [('product_id', '=', id),('order_id','in',sale_order_search),('state','!=','cancel')], context=context)
            elif isinstance(customer_id,str):
                current_values = self.browse(cr,uid,ids[0])
                customer_id = current_values.customer_id.id
                from_date = current_values.from_date
                to_date = current_values.to_date
                sale_order_search =sale_order_obj.search(cr,uid,[('partner_id','=',customer_id),('date_order','>=',from_date),('date_order','<=',to_date)])
                for id in ids:
                    solines_pool = self.pool.get('sale.order.line')
                    result[id] = solines_pool.search(cr, uid, [('product_id', '=', id),('order_id','in',sale_order_search),('state','!=','cancel')], context=context)
            return result
        elif not ids:
            pass

    def get_product_available(self, cr, uid, ids, context=None):
        """ Finds whether product is available or not in particular warehouse.
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        
        location_obj = self.pool.get('stock.location')
        warehouse_obj = self.pool.get('stock.warehouse')
        shop_obj = self.pool.get('sale.shop')
        
        states = context.get('states',[])
        what = context.get('what',())
        if not ids:
            ids = self.search(cr, uid, [])
        res = {}.fromkeys(ids, 0.0)
        if not ids:
            return res

        # if context.get('shop', False):
        #     warehouse_id = shop_obj.read(cr, uid, int(context['shop']), ['warehouse_id'])['warehouse_id'][0]
        #     if warehouse_id:
        #         context['warehouse'] = warehouse_id

        if context.get('warehouse', False):
            lot_id = warehouse_obj.read(cr, uid, int(context['warehouse']), ['lot_stock_id'])['lot_stock_id'][0]
            if lot_id:
                context['location'] = lot_id

        if context.get('location', False):
            if type(context['location']) == type(1):
                location_ids = [context['location']]
            elif type(context['location']) in (type(''), type(u'')):
                location_ids = location_obj.search(cr, uid, [('name','ilike',context['location'])], context=context)
            else:
                location_ids = context['location']
        else:
            location_ids = []
            wids = warehouse_obj.search(cr, uid, [], context=context)
            if not wids:
                return res
            for w in warehouse_obj.browse(cr, uid, wids, context=context):
                location_ids.append(w.lot_stock_id.id)

        # build the list of ids of children of the location given by id
        if context.get('compute_child',True):
            child_location_ids = location_obj.search(cr, uid, [('location_id', 'child_of', location_ids)])
            location_ids = child_location_ids or location_ids
        
        # this will be a dictionary of the product UoM by product id
        product2uom = {}
        uom_ids = []
        for product in self.read(cr, uid, ids, ['uom_id'], context=context):
            product2uom[product['id']] = product['uom_id'][0]
            uom_ids.append(product['uom_id'][0])
        # this will be a dictionary of the UoM resources we need for conversion purposes, by UoM id
        uoms_o = {}
        for uom in self.pool.get('product.uom').browse(cr, uid, uom_ids, context=context):
            uoms_o[uom.id] = uom

        results = []
        results2 = []

        from_date = context.get('from_date',False)
        to_date = context.get('to_date',False)
        date_str = False
        date_values = False
        where = [tuple(location_ids),tuple(location_ids),tuple(ids),tuple(states)]
        if from_date and to_date:
            date_str = "date>=%s and date<=%s"
            where.append(tuple([from_date]))
            where.append(tuple([to_date]))
        elif from_date:
            date_str = "date>=%s"
            date_values = [from_date]
        elif to_date:
            date_str = "date<=%s"
            date_values = [to_date]
        if date_values:
            where.append(tuple(date_values))

        prodlot_id = context.get('prodlot_id', False)
        prodlot_clause = ''
        if prodlot_id:
            prodlot_clause = ' and prodlot_id = %s '
            where += [prodlot_id]

        # TODO: perhaps merge in one query.
        if 'in' in what:
            # all moves from a location out of the set to a location in the set
            cr.execute(
                'select sum(product_qty), product_id, product_uom '\
                'from stock_move '\
                'where location_id NOT IN %s '\
                'and location_dest_id IN %s '\
                'and product_id IN %s '\
                'and state IN %s ' + (date_str and 'and '+date_str+' ' or '') +' '\
                + prodlot_clause + 
                'group by product_id,product_uom',tuple(where))
            results = cr.fetchall()
        if 'out' in what:
            # all moves from a location in the set to a location out of the set
            cr.execute(
                'select sum(product_qty), product_id, product_uom '\
                'from stock_move '\
                'where location_id IN %s '\
                'and location_dest_id NOT IN %s '\
                'and product_id  IN %s '\
                'and state in %s ' + (date_str and 'and '+date_str+' ' or '') + ' '\
                + prodlot_clause + 
                'group by product_id,product_uom',tuple(where))
            results2 = cr.fetchall()
            
        # Get the missing UoM resources
        uom_obj = self.pool.get('product.uom')
        uoms = map(lambda x: x[2], results) + map(lambda x: x[2], results2)
        if context.get('uom', False):
            uoms += [context['uom']]
        uoms = filter(lambda x: x not in uoms_o.keys(), uoms)
        if uoms:
            uoms = uom_obj.browse(cr, uid, list(set(uoms)), context=context)
            for o in uoms:
                uoms_o[o.id] = o
                
        #TOCHECK: before change uom of product, stock move line are in old uom.
        context.update({'raise-exception': False})
        # Count the incoming quantities
        for amount, prod_id, prod_uom in results:
            amount = uom_obj._compute_qty_obj(cr, uid, uoms_o[prod_uom], amount,
                     uoms_o[context.get('uom', False) or product2uom[prod_id]], context=context)
            res[prod_id] += amount
        # Count the outgoing quantities
        for amount, prod_id, prod_uom in results2:
            amount = uom_obj._compute_qty_obj(cr, uid, uoms_o[prod_uom], amount,
                    uoms_o[context.get('uom', False) or product2uom[prod_id]], context=context)
            res[prod_id] -= amount
        return res

    _columns = {
        'lst_price' : fields.function(_product_lst_price, type='float', string='Public Price', digits_compute=dp.get_precision('Product Price')),
        'product_color' : fields.char('Color', size=64, select=True),
        #'product_brand' : fields.char('Brand', size=64, select=True),
        #'product_brand' : fields.selection([('zeeva','Zeeva'),('muve_acoustics','Muve Acoustics'),('digital_essentials','Digital Essentials'),('propella','Propella')],'Product Brand'),
        #'sub_brand': fields.selection([('barbie','Barbie'),('hot_wheels','Hot Wheels'),('monster_high','Monster High'),('max_steel','Max Steel'),('chhota_bheem','Chhota Bheem')],'Sub Brand'),
        'product_brand': fields.many2one('product.brand','Product Brand'),
        'sub_brand': fields.many2one('product.brand','Sub Brand'),
        'subbrand_visible': fields.boolean('Sub Brand Visible'),
        'product_mrp': fields.float('MRP'),
        'vat': fields.float('VAT (in %)'),
        'image_ids': fields.one2many('product.image', 'product_image_id', 'Product images'),
        'image': fields.binary("Image",
            help="Finished product - full image"),
        'image_small': fields.binary("Small-size Image",
            help="Finished product - small size image with a width of 64px"),
        'no_of_items': fields.selection([('2','2'),('3','3')], 'No of Items'),
        'packaging_information': fields.selection([('withpackaging','With Packaging'),('withoutpackaging','Without Packaging')], 'Packaging Information'),
        'raw_approval_flag': fields.boolean('Raw product approved'),
        'manager_fields': fields.function(_product_check_permission, type='boolean', string='Manager'),
        #######################Differentiate Between EXpense Products
        'expense_category': fields.boolean('Expense Category'),
        #########Details Tab Headphone Information
        ####################Section 1
        'description1': fields.text('Description',translate=False),
        'headphone_impedance': fields.selection([('16','16 Ohms'),
                                                ('32','32 Ohms')], 'Impedance'),
        'headphone_freq_min': fields.integer('Frequency min'),
        'headphone_freq_min_dimensions': fields.char('Frequency min dimensions',size=30),
        'headphone_freq_max': fields.integer('Frequency max'),
        'headphone_freq_max_dimensions': fields.char('Frequency max dimensions',size=30),
        'headphone_sensitivity': fields.selection([('85','85 dB'),
                                                   ('96','96 dB'),
                                                   ('100','100 dB'),
                                                   ('102','102 dB'),
                                                   ('110','110 dB')], 'Sensitivity'),
        'headphone_band_primary': fields.selection([('plastic','Plastic'),('metal','Metal'),('leather','Leather'),('pu','PU Leather'),('mesh','Fabric Mesh')], 'Headband Material'),
        'headphone_band_secondary': fields.selection([('plastic','Plastic'),('metal','Metal'),('leather','Leather'),('pu','PU Leather'),('mesh','Fabric Mesh')], 'Headband Material'),
        'headphone_joint_primary': fields.selection([('plastic','Plastic'),('metal','Metal'),('leather','Leather'),('pu','PU Leather')], 'Mechanical Joints Material'),
        'headphone_joint_secondary': fields.selection([('plastic','Plastic'),('metal','Metal'),('leather','Leather'),('pu','PU Leather')], 'Mechanical Joints Material'),
        'headphone_shell_primary': fields.selection([('plastic','Plastic'),('metal','Metal'),('leather','Leather'),('pu','PU Leather')], 'Shells Material'),
        'headphone_shell_secondary': fields.selection([('plastic','Plastic'),('metal','Metal'),('leather','Leather'),('pu','PU Leather')], 'Shells Material'),
        
        'headphone_driver_diameter': fields.selection([('27','27 mm'),
                                                   ('30','30 mm'),
                                                   ('40','40 mm'),
                                                   ('50','50 mm'),
                                                   ('57','57 mm')], 'Driver Diameter'),
        
        'headphone_driver_type': fields.selection([('dynamic','Dynamic')], 'Driver Type'),
        'headphone_cord_length': fields.float('Cord Length', digits=(12, 1)),
        'headphone_cord_length_dimensions': fields.char('Cord Length Dimensions',size=30),
        'headphone_cord_type': fields.char('Cord Type',size=128),
        'headphone_cord_addons': fields.selection([('no','None'),
                                                  ('mic','Microphone'),
                                                  ('vol','Volume control'),
                                                  ('both','Volume control + Mic.')], 'Cord Add Ons'),                          
        'headphone_plug_type': fields.selection([('no','None'),
                                                ('lsh','L-shaped'),
                                                ('ssh','Straight-shaped')], 'Plug Type'),
        'headphone_plug_plating': fields.selection([('gplated','Gold plated'),
                                                   ('gcoated','Gold coated'),
                                                   ('nplated','Nickel plated')], 'Plug Plating'),
        #######################Bluetooth Section
        'headphone_bt': fields.selection([('yes','Yes'),
                                        ('no','No')], 'Bluetooth'),
        'headphone_bt_callerid': fields.selection([('yes','Yes'),
                                                ('no','No')], 'Caller ID Recognition'), 
        'headphone_bt_version': fields.char('Bluetooth Version', size=128),
        'headphone_bt_range': fields.char('Bluetooth Range', size=128),
        'headphone_bt_supplier': fields.char('Bluetooth Chip Supplier', size=128),
        'bluetooth_section_visible': fields.boolean('Bluetooth Section'),

        ############################Power Bank Fields
        'pb_microusb': fields.boolean('Micro USB'),
        'fast_charging': fields.boolean('Fast Charging'),
        'led_flash_light': fields.boolean('LED Flash Light'),
        'overcharge_protection': fields.boolean('Overcharge Protection'),
        'power_capacity_display': fields.boolean('Power Capacity Display'),
        'pb_capacity': fields.char('Capacity', size=64),
        'pb_unit_size_l': fields.integer('Unit Size L'),
        'pb_unit_size_w': fields.integer('Unit Size W'),
        'pb_unit_size_h': fields.integer('Unit Size H'),
        'pb_input': fields.char('Input', size=64),
        'pb_output_type': fields.selection([('single','Single'), ('dual','Dual'),('triple','Triple')], 'Output Type'),
        'pb_output1': fields.char('Output', size=64),
        'pb_output2': fields.char('Output 2', size=64),
        'pb_output3': fields.char('Output 3',size=64),
        'powerbank_section_visible': fields.boolean('Power Bank Section'),

        ##################################Batteries Fields
        'battery_capacity': fields.char('Battery Capacity', size=64),
        'battery_brand': fields.char('Battery Brand', size=64),
        'model_no': fields.char('Model', size=64),
        'batteries_section_visible': fields.boolean('Batteries Section'),

        #######################Unit Measurement Fields
        'product_id_section1': fields.many2one('product.product','Product'),
        'unit_net': fields.float('Unit Net Weight1', digits_compute=dp.get_precision('Stock Weight'), help="The unit net weight in Kg."),
        'unit_l': fields.float('Unit Length1'),
        'unit_w': fields.float('Unit Width1'),
        'unit_h': fields.float('Unit Height1'),
        'unit_cbm': fields.function(_compute_cbm, string='Unit CBM', type='float', digits_compute=dp.get_precision('Product Volume')),
        'unit_cuft': fields.function(_compute_cuft, string='Unit CUFT', type='float', digits_compute=dp.get_precision('Product Volume')),

        ###############Unit + Packing Fields
        'pack_gross': fields.float('Package Gross Weight1', digits_compute=dp.get_precision('Stock Weight'), help="The unit+package gross weight in Kg."),
        'pack_l': fields.float('Package Length1'),
        'pack_w': fields.float('Package Width1'),
        'pack_h': fields.float('Package Height1'),
        'pack_cbm': fields.function(_compute_cbm, string='Package CBM', type='float', digits_compute=dp.get_precision('Product Volume')),
        'pack_cuft': fields.function(_compute_cuft, string='Package CUFT', type='float', digits_compute=dp.get_precision('Product Volume')),

        ##########Inner Carton Fields
        'inner_gross': fields.float('Inner Carton Gross Weight1', digits_compute=dp.get_precision('Stock Weight'), help="The inner carton gross weight in Kg."),
        'inner_net': fields.float('Inner Carton Net Weight1', digits_compute=dp.get_precision('Stock Weight'), help="The inner carton net weight in Kg."),  
        'inner_l': fields.float('Inner Carton Length1'),
        'inner_w': fields.float('Inner Carton Width1'),
        'inner_h': fields.float('Inner Carton Height1'),   
        'inner_cbm': fields.function(_compute_cbm, string='Inner Carton CBM', type='float', digits_compute=dp.get_precision('Product Volume')),
        'inner_cuft': fields.function(_compute_cuft, string='Inner Carton CUFT', type='float', digits_compute=dp.get_precision('Product Volume')),       
        'pack_inner': fields.integer('Inner Carton1' ),
        'pack_inner_barcode': fields.char('Inner Carton Barcode1' ),

        ##################Export Carton Fields 
        'export_gross': fields.float('Export Carton Gross Weight1', digits_compute=dp.get_precision('Stock Weight'), help="The export carton gross weight in Kg."),
        'export_net': fields.float('Export Carton Net Weight1', digits_compute=dp.get_precision('Stock Weight'), help="The export carton net weight in Kg."),      
        'export_l': fields.float('Export Carton Length1'),
        'export_w': fields.float('Export Carton Width1'),
        'export_h': fields.float('Export Carton Height1'),       
        'export_cbm': fields.function(_compute_cbm, string='Export Carton CBM', type='float', digits_compute=dp.get_precision('Product Volume')),
        'export_cuft': fields.function(_compute_cuft, string='Export Carton CUFT', type='float', digits_compute=dp.get_precision('Product Volume')),       
        'pack_export': fields.integer('Export Carton1'),
        'pack_export_barcode': fields.char('Export Carton Barcode1'),
        'pack_remarks': fields.text('Additional Packing Information1'),

        ####################Section 2
        #######################Unit Measurement Fields
        'product_id_section2': fields.many2one('product.product','Product'),
        'unit_net_section2': fields.float('Unit Net Weight', digits_compute=dp.get_precision('Stock Weight'), help="The unit net weight in Kg."),
        'unit_l_section2': fields.float('Unit Length'),
        'unit_w_section2': fields.float('Unit Width' ),
        'unit_h_section2': fields.float('Unit Height'),
        'unit_cbm_section2': fields.function(_compute_cbm, string='Unit CBM', type='float', digits_compute=dp.get_precision('Product Volume')),
        'unit_cuft_section2': fields.function(_compute_cuft, string='Unit CUFT', type='float', digits_compute=dp.get_precision('Product Volume')),

        ###############Unit + Packing Fields
        'pack_gross_section2': fields.float('Package Gross Weight', digits_compute=dp.get_precision('Stock Weight'), help="The unit+package gross weight in Kg."),
        'pack_l_section2': fields.float('Package Length'),
        'pack_w_section2': fields.float('Package Width'),
        'pack_h_section2': fields.float('Package Height'),
        'pack_cbm_section2': fields.function(_compute_cbm, string='Package CBM', type='float', digits_compute=dp.get_precision('Product Volume')),
        'pack_cuft_section2': fields.function(_compute_cuft, string='Package CUFT', type='float', digits_compute=dp.get_precision('Product Volume')),

        ##########Inner Carton Fields
        'inner_gross_section2': fields.float('Inner Carton Gross Weight', digits_compute=dp.get_precision('Stock Weight'), help="The inner carton gross weight in Kg."),
        'inner_net_section2': fields.float('Inner Carton Net Weight', digits_compute=dp.get_precision('Stock Weight'), help="The inner carton net weight in Kg."),  
        'inner_l_section2': fields.float('Inner Carton Length'),
        'inner_w_section2': fields.float('Inner Carton Width'),
        'inner_h_section2': fields.float('Inner Carton Height'),   
        'inner_cbm_section2': fields.function(_compute_cbm, string='Inner Carton CBM', type='float', digits_compute=dp.get_precision('Product Volume')),
        'inner_cuft_section2': fields.function(_compute_cuft, string='Inner Carton CUFT', type='float', digits_compute=dp.get_precision('Product Volume')),       
        'pack_inner_section2': fields.integer('Inner Carton'),
        'pack_inner_barcode_section2': fields.char('Inner Carton Barcode'),

        ##################Export Carton Fields 
        'export_gross_section2': fields.float('Export Carton Gross Weight', digits_compute=dp.get_precision('Stock Weight'), help="The export carton gross weight in Kg."),
        'export_net_section2': fields.float('Export Carton Net Weight', digits_compute=dp.get_precision('Stock Weight'), help="The export carton net weight in Kg."),      
        'export_l_section2': fields.float('Export Carton Length'),
        'export_w_section2': fields.float('Export Carton Width'),
        'export_h_section2': fields.float('Export Carton Height'),       
        'export_cbm_section2': fields.function(_compute_cbm, string='Export Carton CBM', type='float', digits_compute=dp.get_precision('Product Volume')),
        'export_cuft_section2': fields.function(_compute_cuft, string='Export Carton CUFT', type='float', digits_compute=dp.get_precision('Product Volume')),       
        'pack_export_section2': fields.integer('Export Carton'),
        'pack_export_barcode_section2': fields.char('Export Carton Barcode'),
        'pack_remarks_section2': fields.text('Additional Packing Information'),

        ####################Section 3
        #######################Unit Measurement Fields
        'product_id_section3': fields.many2one('product.product','Product'),
        'unit_net_section3': fields.float('Unit Net Weight', digits_compute=dp.get_precision('Stock Weight'), help="The unit net weight in Kg."),
        'unit_l_section3': fields.float('Unit Length'),
        'unit_w_section3': fields.float('Unit Width'),
        'unit_h_section3': fields.float('Unit Height'),
        'unit_cbm_section3': fields.function(_compute_cbm, string='Unit CBM', type='float', digits_compute=dp.get_precision('Product Volume')),
        'unit_cuft_section3': fields.function(_compute_cuft, string='Unit CUFT', type='float', digits_compute=dp.get_precision('Product Volume')),

        ###############Unit + Packing Fields
        'pack_gross_section3': fields.float('Package Gross Weight', digits_compute=dp.get_precision('Stock Weight'), help="The unit+package gross weight in Kg."),
        'pack_l_section3': fields.float('Package Length'),
        'pack_w_section3': fields.float('Package Width'),
        'pack_h_section3': fields.float('Package Height'),
        'pack_cbm_section3': fields.function(_compute_cbm, string='Package CBM', type='float', digits_compute=dp.get_precision('Product Volume')),
        'pack_cuft_section3': fields.function(_compute_cuft, string='Package CUFT', type='float', digits_compute=dp.get_precision('Product Volume')),

        ##########Inner Carton Fields
        'inner_gross_section3': fields.float('Inner Carton Gross Weight', digits_compute=dp.get_precision('Stock Weight'), help="The inner carton gross weight in Kg."),
        'inner_net_section3': fields.float('Inner Carton Net Weight', digits_compute=dp.get_precision('Stock Weight'), help="The inner carton net weight in Kg."),  
        'inner_l_section3': fields.float('Inner Carton Length'),
        'inner_w_section3': fields.float('Inner Carton Width'),
        'inner_h_section3': fields.float('Inner Carton Height'),   
        'inner_cbm_section3': fields.function(_compute_cbm, string='Inner Carton CBM', type='float', digits_compute=dp.get_precision('Product Volume')),
        'inner_cuft_section3': fields.function(_compute_cuft, string='Inner Carton CUFT', type='float', digits_compute=dp.get_precision('Product Volume')),       
        'pack_inner_section3': fields.integer('Inner Carton'),
        'pack_inner_barcode_section3': fields.char('Inner Carton Barcode'),

        ##################Export Carton Fields 
        'export_gross_section3': fields.float('Export Carton Gross Weight', digits_compute=dp.get_precision('Stock Weight'), help="The export carton gross weight in Kg."),
        'export_net_section3': fields.float('Export Carton Net Weight', digits_compute=dp.get_precision('Stock Weight'), help="The export carton net weight in Kg."),      
        'export_l_section3': fields.float('Export Carton Length'),
        'export_w_section3': fields.float('Export Carton Width'),
        'export_h_section3': fields.float('Export Carton Height'),       
        'export_cbm_section3': fields.function(_compute_cbm, string='Export Carton CBM', type='float', digits_compute=dp.get_precision('Product Volume')),
        'export_cuft_section3': fields.function(_compute_cuft, string='Export Carton CUFT', type='float', digits_compute=dp.get_precision('Product Volume')),       
        'pack_export_section3': fields.integer('Export Carton'),
        'pack_export_barcode_section3': fields.char('Export Carton Barcode'),
        'pack_remarks_section3': fields.text('Additional Packing Information'),

        #######################History tab######  
        'saleorderline_ids': fields.function(_get_so_lines, method=True,type='one2many', relation='sale.order.line', string='Sales Order Lines'),
        'customer_id': fields.many2one('res.partner', 'Customer'),
        'from_date': fields.date('From Date'),
        'to_date': fields.date('To Date'),

        ##########################Combo Product Tab#########
        'combo_product': fields.boolean('Combo Product'),
        'combo_productline_id': fields.one2many('combo.product.line','combo_product_id','Combo Products Tree'),
        'total_pieces': fields.function(_no_of_pieces, string='1 set = ', type='float'),
        'no_of_pieces_label': fields.char('no of pieces',size=30),

     }


    #----------------------------------------------------------------------------------------------------------
    # name_get function inherited for description must be seen first and code must be seen later for the product 
    #-----------------------------------------------------------------------------------------------------------
    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []
        def _name_get(d):
            name = d.get('name','')
            code = d.get('default_code',False)
            if code:
                name = '%s [%s]' % (name,code)
            if d.get('variants'):
                name = name + ' - %s' % (d['variants'],)
            return (d['id'], name)

        partner_id = context.get('partner_id', False)
        if partner_id:
            partner_ids = [partner_id, self.pool['res.partner'].browse(cr, user, partner_id, context=context).commercial_partner_id.id]
        else:
            partner_ids = []

        result = []
        for product in self.browse(cr, user, ids, context=context):
            sellers = partner_ids and filter(lambda x: x.name.id in partner_ids, product.seller_ids) or []
            if sellers:
                for s in sellers:
                    mydict = {
                              'id': product.id,
                              'name': s.product_name or product.name,
                              'default_code': s.product_code or product.default_code,
                              'variants': product.variants
                              }
                    result.append(_name_get(mydict))
            else:
                mydict = {
                          'id': product.id,
                          'name': product.name,
                          'default_code': product.default_code,
                          'variants': product.variants
                          }
                result.append(_name_get(mydict))
        return result

    #Function which will return the Barcode is valid or Invalid 
    #------------------------------------------------------------

    def _check_ean_key(self, cr, uid, ids, context=None):
        for product in self.read(cr, uid, ids, ['ean13'], context=context):
            res = check_ean(product['ean13'])
        return res

    _constraints = [(_check_ean_key, 'You provided an invalid "Barcode" reference.', ['ean13'])]

    _defaults={
            'headphone_freq_min_dimensions' : 'Hz -',
            'headphone_freq_max_dimensions' : 'KHz',
            'headphone_cord_length_dimensions': 'm',
            'packaging_information': 'withpackaging',
            'no_of_pieces_label': 'no of pieces',
            'raw_approval_flag': False,
            'expense_category': False,
            'active': False,
    }

    def onchange_categ_id(self,cr,uid,ids,categ_id):
        result={}
        append_categ_name=[]
        categ_name = 'Bluetooth'
        batteries_categ_name = 'Batter'
        power_bank_categ_name = 'Bank'
        if categ_id:
            cr.execute('select name from product_category where id=%s',(categ_id,))
            category_name = map(lambda x: x[0], cr.fetchall())
            string_category_name = str(category_name)
            if power_bank_categ_name in string_category_name:
                result['powerbank_section_visible'] = True
            else:
                result['powerbank_section_visible'] = False
            if batteries_categ_name in string_category_name:
                result['batteries_section_visible'] = True
            else:
                result['batteries_section_visible'] = False
        # category_name_id=category_name[0]
        # category_name_str = str(category_name_id)
        # categ_name_split = list(categ_name)
        # category_name_str_split = list(category_name_str)
        # for categ_name_split_id in categ_name_split:
        #     if categ_name_split_id in category_name_str_split:
        #         append_categ_name+=categ_name_split_id
        # if len(append_categ_name) == 9:
        #     result['bluetooth_section_visible'] = True
        # else:
        #     result['bluetooth_section_visible'] = False
        return {'value':result}


    #----------------------------------------------------------------------
    # Onchange Written for the Product Brands and the Sub Brands Visibility
    #----------------------------------------------------------------------
    def onchange_product_brand(self,cr,uid,ids,product_brand):
        result={}
        product_brand_obj = self.pool.get('product.brand')
        if product_brand:
            search_product_brand_id = product_brand_obj.search(cr,uid,[('parent_id','=',product_brand)])
            if search_product_brand_id:
                result['subbrand_visible'] = True
            else:
                result['subbrand_visible'] = False
        return {'value':result}

    #-------------------------------------------------------------------------
    #Writen an onchange for Filtering into the History tab in the Product Form
    #-------------------------------------------------------------------------
    def onchange_from_date(self,cr,uid,ids,customer_id,from_date,to_date):
        result={}
        if from_date and to_date:
            if from_date > to_date:
                raise osv.except_osv(('Warning!!'),('From Date Must Be Greater than To Date.'))
        val = self._get_so_lines(cr,uid,ids,customer_id,from_date,to_date,field_names=None,arg=None, context=None)
        if val:
            for x,y in val.iteritems():
                if y:
                    for o in y:
                        v={'saleorderline_ids' : y}
                        result = {'value': v}
                        return result
                else:
                    v={'saleorderline_ids' : ''}
                    result = {'value': v}
                    return result
        else:
            return result

    #--------------------------------------------------------------------------------------------------
    #Create and Write Function is used for same Name of Product and for warning shippedqty greater than billedqty
    #--------------------------------------------------------------------------------------------------
    def create(self, cr, uid, vals, context=None):
        res_id = super(product_product, self).create(cr, uid, vals, context)
        if isinstance(res_id, list):
            main_form_id = res_id[0]
        else:
            main_form_id = res_id
        if vals.has_key('combo_productline_id'):
            if vals['combo_productline_id']:
                combo_line_list_values = vals['combo_productline_id']
                for combo_list_id in combo_line_list_values:
                    combo_id = combo_list_id[2]
                    if combo_id.has_key('shipped_quantity') and combo_id.has_key('billed_quantity'):
                        shipped_quantity = combo_id.get('shipped_quantity')
                        billed_quantity = combo_id.get('billed_quantity')
                        if shipped_quantity < billed_quantity:
                            raise osv.except_osv(_('Warning!'),_('Shipped Quantity must be greater than Billed Quantity.'))
        if vals['name']:
            product_name = vals['name']
            search_name_id = self.search(cr,uid,[('name','=',product_name),('id','!=',res_id)])
            if search_name_id:
                raise osv.except_osv(_('Warning!'), _('Product Name Must Be Different For Each Product.'))
        return res_id

    def write(self, cr, uid, ids, vals, context=None):
        res = super(product_product, self).write(cr, uid, ids, vals, context=context)
        if isinstance(ids, list):
            main_id = ids[0]
        else:
            main_id = ids
        combo_product_line_obj = self.pool.get('combo.product.line')
        if vals.has_key('combo_productline_id'):
            search_line_id = combo_product_line_obj.search(cr,uid,[('combo_product_id','=',main_id)])
            search_line_browse= combo_product_line_obj.browse(cr,uid,search_line_id)
            for search_line_browse_id in search_line_browse:
                search_main_id = search_line_browse_id.id
                shipped_quantity = search_line_browse_id.shipped_quantity
                billed_quantity = search_line_browse_id.billed_quantity
                if shipped_quantity < billed_quantity:
                    raise osv.except_osv(_('Warning!'),_('Shipped Quantity must be greater than Billed Quantity.'))
        return res

    #---------------------------------------------------------
    #Onchange for the Product section 1 in details tab
    #---------------------------------------------------------
    def onchange_product_id_section1(self,cr,uid,ids,product_id_section1):
        result = {}
        
        if product_id_section1:
            product_product_obj = self.browse(cr, uid, product_id_section1)
            
            if product_product_obj:
                
                value={
                    'unit_net': product_product_obj.unit_net,
                    'unit_l': product_product_obj.unit_l,
                    'unit_w': product_product_obj.unit_w,
                    'unit_h': product_product_obj.unit_h,
                    'unit_cbm': product_product_obj.unit_cbm,
                    'unit_cuft': product_product_obj.unit_cuft,

                    ###############Unit + Packing Fields
                    'pack_gross': product_product_obj.pack_gross,
                    'pack_l': product_product_obj.pack_l,
                    'pack_w': product_product_obj.pack_w,
                    'pack_h': product_product_obj.pack_h,
                    'pack_cbm': product_product_obj.pack_cbm,
                    'pack_cuft': product_product_obj.pack_cuft,

                    ##########Inner Carton Fields
                    'inner_gross': product_product_obj.inner_gross,
                    'inner_net': product_product_obj.inner_net,
                    'inner_l': product_product_obj.inner_l,
                    'inner_w': product_product_obj.inner_w,
                    'inner_h': product_product_obj.inner_h,
                    'inner_cbm': product_product_obj.inner_cbm,
                    'inner_cuft': product_product_obj.inner_cuft,
                    'pack_inner': product_product_obj.pack_inner,
                    'pack_inner_barcode': product_product_obj.pack_inner_barcode,

                    ##################Export Carton Fields 
                    'export_gross': product_product_obj.export_gross,
                    'export_net': product_product_obj.export_net,
                    'export_l': product_product_obj.export_l,
                    'export_w': product_product_obj.export_w,
                    'export_h': product_product_obj.export_h,
                    'export_cbm': product_product_obj.export_cbm,
                    'export_cuft': product_product_obj.export_cuft,
                    'pack_export': product_product_obj.pack_export,
                    'pack_export_barcode': product_product_obj.pack_export_barcode,
                    ###################Packaging Information
                    'pack_remarks': product_product_obj.pack_remarks
                }
                
            result = {'value': value}
        
        return result

    #---------------------------------------------------------
    #Onchange for the Product section 2 in details tab
    #---------------------------------------------------------
    def onchange_product_id_section2(self,cr,uid,ids,product_id_section2):
        result = {}
        
        if product_id_section2:
            product_product_obj = self.browse(cr, uid, product_id_section2)
            
            if product_product_obj:
                
                value={
                    'unit_net_section2': product_product_obj.unit_net,
                    'unit_l_section2': product_product_obj.unit_l,
                    'unit_w_section2': product_product_obj.unit_w,
                    'unit_h_section2': product_product_obj.unit_h,
                    'unit_cbm_section2': product_product_obj.unit_cbm,
                    'unit_cuft_section2': product_product_obj.unit_cuft,

                    ###############Unit + Packing Fields
                    'pack_gross_section2': product_product_obj.pack_gross,
                    'pack_l_section2': product_product_obj.pack_l,
                    'pack_w_section2': product_product_obj.pack_w,
                    'pack_h_section2': product_product_obj.pack_h,
                    'pack_cbm_section2': product_product_obj.pack_cbm,
                    'pack_cuft_section2': product_product_obj.pack_cuft,

                    ##########Inner Carton Fields
                    'inner_gross_section2': product_product_obj.inner_gross,
                    'inner_net_section2': product_product_obj.inner_net,
                    'inner_l_section2': product_product_obj.inner_l,
                    'inner_w_section2': product_product_obj.inner_w,
                    'inner_h_section2': product_product_obj.inner_h,
                    'inner_cbm_section2': product_product_obj.inner_cbm,
                    'inner_cuft_section2': product_product_obj.inner_cuft,
                    'pack_inner_section2': product_product_obj.pack_inner,
                    'pack_inner_barcode_section2': product_product_obj.pack_inner_barcode,

                    ##################Export Carton Fields 
                    'export_gross_section2': product_product_obj.export_gross,
                    'export_net_section2': product_product_obj.export_net,
                    'export_l_section2': product_product_obj.export_l,
                    'export_w_section2': product_product_obj.export_w,
                    'export_h_section2': product_product_obj.export_h,
                    'export_cbm_section2': product_product_obj.export_cbm,
                    'export_cuft_section2': product_product_obj.export_cuft,
                    'pack_export_section2': product_product_obj.pack_export,
                    'pack_export_barcode_section2': product_product_obj.pack_export_barcode,

                    ###################Packaging Information
                    'pack_remarks_section2': product_product_obj.pack_remarks,
                }
                
            result = {'value': value}
        
        return result

    #---------------------------------------------------------
    #Onchange for the Product section 3 in details tab
    #---------------------------------------------------------
    def onchange_product_id_section3(self,cr,uid,ids,product_id_section3):
        result = {}
        
        if product_id_section3:
            product_product_obj = self.browse(cr, uid, product_id_section3)
            
            if product_product_obj:
                
                value={
                    'unit_net_section3': product_product_obj.unit_net,
                    'unit_l_section3': product_product_obj.unit_l,
                    'unit_w_section3': product_product_obj.unit_w,
                    'unit_h_section3': product_product_obj.unit_h,
                    'unit_cbm_section3': product_product_obj.unit_cbm,
                    'unit_cuft_section3': product_product_obj.unit_cuft,

                    ###############Unit + Packing Fields
                    'pack_gross_section3': product_product_obj.pack_gross,
                    'pack_l_section3': product_product_obj.pack_l,
                    'pack_w_section3': product_product_obj.pack_w,
                    'pack_h_section3': product_product_obj.pack_h,
                    'pack_cbm_section3': product_product_obj.pack_cbm,
                    'pack_cuft_section3': product_product_obj.pack_cuft,

                    ##########Inner Carton Fields
                    'inner_gross_section3': product_product_obj.inner_gross,
                    'inner_net_section3': product_product_obj.inner_net,
                    'inner_l_section3': product_product_obj.inner_l,
                    'inner_w_section3': product_product_obj.inner_w,
                    'inner_h_section3': product_product_obj.inner_h,
                    'inner_cbm_section3': product_product_obj.inner_cbm,
                    'inner_cuft_section3': product_product_obj.inner_cuft,
                    'pack_inner_section3': product_product_obj.pack_inner,
                    'pack_inner_barcode_section3': product_product_obj.pack_inner_barcode,

                    ##################Export Carton Fields 
                    'export_gross_section3': product_product_obj.export_gross,
                    'export_net_section3': product_product_obj.export_net,
                    'export_l_section3': product_product_obj.export_l,
                    'export_w_section3': product_product_obj.export_w,
                    'export_h_section3': product_product_obj.export_h,
                    'export_cbm_section3': product_product_obj.export_cbm,
                    'export_cuft_section3': product_product_obj.export_cuft,
                    'pack_export_section3': product_product_obj.pack_export,
                    'pack_export_barcode_section3': product_product_obj.pack_export_barcode,

                    ###################Packaging Information
                    'pack_remarks_section3': product_product_obj.pack_remarks,
                }
                
            result = {'value': value}
        
        return result

    def submit_to_management(self,cr,uid,ids,context=None):
        o = self.browse(cr,uid,ids[0])
        main_form_id = o.id
        product_code = o.default_code
        product_name = o.name
        subscribe_ids = []
        zeeva_ind_management = ['nitin','akshay']
        subscribe_ids += self.pool.get('res.users').search(cr, SUPERUSER_ID, [('login','in',zeeva_ind_management)])
        self.message_subscribe_users(cr, SUPERUSER_ID, [o.id], user_ids=subscribe_ids, context=context)
        message1 = _("<b>Status: Draft --> Submitted to Management</b>")
        self.message_post(cr, uid, ids, body = message1, type='comment', subtype='mt_comment', context = context)
        message = _("<b>Dear Sir,<br/><br/>I kindly request you to approve the Product [%s] %s.</b>") % (product_code,product_name)
        self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)
        self.write(cr,uid,main_form_id,{'state': 'submit_to_management','raw_approval_flag': False,'active':False})
        return True

    def approved(self,cr,uid,ids,context=None):
        o = self.browse(cr,uid,ids[0])
        main_form_id = o.id
        product_code = o.default_code
        product_name = o.name
        subscribe_ids = []
        zeeva_ind_management = ['nitin','akshay']
        subscribe_ids += self.pool.get('res.users').search(cr, SUPERUSER_ID, [('login','in',zeeva_ind_management)])
        self.message_subscribe_users(cr, SUPERUSER_ID, [o.id], user_ids=subscribe_ids, context=context)
        message1 = _("<b>Status: Submitted to Management --> Approved</b>")
        self.message_post(cr, uid, ids, body = message1, type='comment', subtype='mt_comment', context = context)
        message = _("<b>Hi,<br/><br/>This Product [%s] %s has been Approved.</b>") % (product_code,product_name)
        self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)
        self.write(cr,uid,main_form_id,{'state': 'sellable','raw_approval_flag': True,'active':True})
        return True

    def reset_to_draft(self,cr,uid,ids,context=None):
        o = self.browse(cr,uid,ids[0])
        main_form_id = o.id
        state = o.state
        subscribe_ids = []
        zeeva_ind_management = ['nitin','akshay']
        subscribe_ids += self.pool.get('res.users').search(cr, SUPERUSER_ID, [('login','in',zeeva_ind_management)])
        self.message_subscribe_users(cr, SUPERUSER_ID, [o.id], user_ids=subscribe_ids, context=context)
        if state == 'sellable':
            message = _("<b>Status: Approved --> Draft</b>")
            self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)
        else:
            message = _("<b>Status: Submitted to Management --> Draft</b>")
            self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)
        self.write(cr,uid,main_form_id,{'state': 'draft','raw_approval_flag': False,'active':False})
        return True

product_product()

#---------------------------------------------
#Inherited the Sale Order Table
#---------------------------------------------
class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
            #'order_line': fields.one2many('sale.order.line', 'order_id', 'Order Lines', domain=[('invisible_comboproducts', '=', False)],readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
    }

    #------------------------------------------------------
    #Inherited from the Sale Module having sale Order 
    #------------------------------------------------------
    # def action_wait(self, cr, uid, ids, context=None):
    #     sale_order_line_obj = self.pool.get('sale.order.line')
    #     context = context or {}
    #     line_values=[]
    #     for o in self.browse(cr, uid, ids):
    #         main_id =o.id
    #         if not o.order_line:
    #             raise osv.except_osv(_('Error!'),_('You cannot confirm a sales order which has no line.'))
    #         noprod = self.test_no_product(cr, uid, o, context)
    #         if (o.order_policy == 'manual') or noprod:
    #             self.write(cr, uid, [o.id], {'state': 'manual', 'date_confirm': fields.date.context_today(self, cr, uid, context=context)})
    #         else:
    #             self.write(cr, uid, [o.id], {'state': 'progress', 'date_confirm': fields.date.context_today(self, cr, uid, context=context)})
    #         search_product_id = sale_order_line_obj.search(cr,uid,[('order_id','=',main_id)])
    #         for line in sale_order_line_obj.browse(cr,uid,search_product_id):
    #             line_id =line.id
    #             line_values.append(line.id)
    #         self.pool.get('sale.order.line').button_confirm(cr, uid, line_values)
    #     return True

    #------------------------------------------------------
    #Inherited from the Sale Stock Module having sale Order 
    #------------------------------------------------------
    # def action_ship_create(self, cr, uid, ids, context=None):
    #     line_values=[]
    #     sale_order_line_obj = self.pool.get('sale.order.line')
    #     for order in self.browse(cr, uid, ids, context=context):
    #         main_id = order.id
    #         search_product_id = sale_order_line_obj.search(cr,uid,[('order_id','=',main_id)])
    #         for line in sale_order_line_obj.browse(cr,uid,search_product_id):
    #             line_id =line.id
    #             line_values.append(line)
    #     self._create_pickings_and_procurements(cr, uid, order, line_values, None, context=context)
    #     return True

    def create(self, cr, uid, vals, context=None):
        line_values=[]
        main_append = []
        sale_order_line_obj = self.pool.get('sale.order.line')
        combo_product_line = self.pool.get('combo.product.line')
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.order') or '/'
        res_id = super(sale_order, self).create(cr, uid, vals, context=context)
        if isinstance(res_id,list):
            main_form_id = res_id[0]
        else:
            main_form_id = res_id
        if vals['name']:
            so_number = self.browse(cr,uid,main_form_id).name
            zeeva_ind_management = ['nitin','arun']
            subscribe_ids = []
            subscribe_ids += self.pool.get('res.users').search(cr, SUPERUSER_ID, [('login','in',zeeva_ind_management)])
            self.message_subscribe_users(cr, SUPERUSER_ID, [main_form_id], user_ids=subscribe_ids, context=context)
            message = _("<b>Dear Sir,<br/><br/> The Sale Order %s has been created.</b>") % (so_number)
            self.message_post(cr, uid, main_form_id, body = message, type='comment', subtype='mt_comment', context = context)
        if vals['order_line']:
            search_product_id = sale_order_line_obj.search(cr,uid,[('order_id','=',res_id)])
            order_line_list_values = vals['order_line']
            for order_line_values in order_line_list_values:
                order_line_values_id = order_line_values[2]
                if order_line_values_id.has_key('product_uom_qty') and order_line_values_id.has_key('product_billed_qty'):
                    product_uom_qty = order_line_values_id.get('product_uom_qty')
                    product_billed_qty = order_line_values_id.get('product_billed_qty')
                    if product_uom_qty < product_billed_qty:
                        raise osv.except_osv(_('Warning!'),_('Shipped Quantity must be greater than Billed Quantity.'))
            # for main_form_id in sale_order_line_obj.browse(cr,uid,search_product_id):
            #     product_id = main_form_id.product_id.id
            #     combo_product = main_form_id.product_id.combo_product
            #     if combo_product:
            #         search_combo_products = combo_product_line.search(cr,uid,[('combo_product_id','=',product_id)])
            #         for line_combo_product in combo_product_line.browse(cr,uid,search_combo_products):
            #             sale_order_line_obj.create(cr,uid,{'product_id':line_combo_product.product_id.id,'name':line_combo_product.product_id.name,'product_uom_qty':line_combo_product.shipped_quantity,'product_billed_qty':line_combo_product.billed_quantity,'order_id':res_id,'invisible_comboproducts':True})
        return res_id

    def write(self, cr, uid, ids, vals, context=None):
        res = super(sale_order, self).write(cr, uid, ids, vals, context=context)
        if isinstance(ids,list):
            main_id = ids[0]
        else:
            main_id = ids
        sale_order_line_obj = self.pool.get('sale.order.line')
        product_customer_saleprice_obj = self.pool.get('product.customer.saleprice')
        if vals.has_key('partner_id'):
            search_line_id = sale_order_line_obj.search(cr,uid,[('order_id','=',main_id)])
            print "ssssssssssssssssssssssssssssaaaaaaa",search_line_id
            partner_id = vals.get('partner_id')
            search_line_browse= sale_order_line_obj.browse(cr,uid,search_line_id)
            for search_line_browse_id in search_line_browse:
                sale_price = search_line_browse_id.sale_price.id
                product_customer_saleprice_obj.write(cr,uid,sale_price,{'customer_id':partner_id})
        if vals.has_key('order_line'):
            search_line_id = sale_order_line_obj.search(cr,uid,[('order_id','=',main_id)])
            search_line_browse= sale_order_line_obj.browse(cr,uid,search_line_id)
            for search_line_browse_id in search_line_browse:
                search_main_id = search_line_browse_id.id
                product_uom_qty = search_line_browse_id.product_uom_qty
                product_billed_qty = search_line_browse_id.product_billed_qty
                if product_uom_qty < product_billed_qty:
                    raise osv.except_osv(_('Warning!'),_('Shipped Quantity must be greater than Billed Quantity.'))
        return res

    #------------------------------------------------------
    #Inherited from the Sale Stock Module having sale Order 
    #------------------------------------------------------
    # def _prepare_order_line_move(self, cr, uid, order, line, picking_id, date_planned, context=None):
    #     location_id = order.shop_id.warehouse_id.lot_stock_id.id
    #     output_id = order.shop_id.warehouse_id.lot_output_id.id
    #     return {
    #         'name': line.name,
    #         'picking_id': picking_id,
    #         'product_id': line.product_id.id,
    #         'date': date_planned,
    #         'date_expected': date_planned,
    #         'product_qty': line.product_uom_qty,
    #         'product_uom': line.product_uom.id,
    #         'product_uos_qty': (line.product_uos and line.product_uos_qty) or line.product_uom_qty,
    #         'product_uos': (line.product_uos and line.product_uos.id)\
    #                 or line.product_uom.id,
    #         'product_packaging': line.product_packaging.id,
    #         'partner_id': line.address_allotment_id.id or order.partner_shipping_id.id,
    #         'location_id': location_id,
    #         'location_dest_id': output_id,
    #         'sale_line_id': line.id,
    #         'tracking_id': False,
    #         'invisible_products': line.invisible_comboproducts,
    #         'state': line.state,
    #         #'state': 'waiting',
    #         'company_id': order.company_id.id,
    #         #'price_unit': line.product_id.standard_price or 0.0
    #         'price_unit': line.price_unit
    #     }


sale_order()



#---------------------------------------------
# Inherited the Default Sale Order Line Module
#---------------------------------------------

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_billed_qty, line.product_id, line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res

    _columns = {
        'create_date': fields.datetime('Created Date', readonly=True, select=True),
        'create_uid': fields.many2one('res.users','Created By',readonly=True, select=True),
        'write_uid': fields.many2one('res.users','Edited By',readonly=True, select=True),
        'write_date': fields.datetime('Edited Date',readonly=True,select=True),
        'sale_price': fields.many2one('product.customer.saleprice','Unit Price'),
        'product_uom_qty': fields.float('Shipped Quantity', digits_compute= dp.get_precision('Product UoS'), required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'product_billed_qty': fields.float('Billed Quantity', digits_compute= dp.get_precision('Product UoS'), required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
        #'invisible_comboproducts': fields.boolean('Invisible Products'),
        
    }

    _defaults={
                'product_billed_qty' : 1,
                #'invisible_comboproducts':False,
    }

# #------------------------------------------------------------------------------------
# # Inherit Default Product Onchange For the Sale Price to Taken from the New Interface
# #------------------------------------------------------------------------------------
#     def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
#             uom=False, qty_uos=0, uos=False, name='', partner_id=False,
#             lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
#         context = context or {}
#         lang = lang or context.get('lang',False)
#         if not  partner_id:
#             raise osv.except_osv(_('No Customer Defined!'), _('Before choosing a product,\n select a customer in the sales form.'))
#         warning = {}
#         product_uom_obj = self.pool.get('product.uom')
#         partner_obj = self.pool.get('res.partner')
#         product_obj = self.pool.get('product.product')
#         ###New Sale Price Interface Object is given###########
#         product_customer_obj = self.pool.get('product.customer')
#         product_customer_saleprice_obj = self.pool.get('product.customer.saleprice')
#         ######################################################
#         context = {'lang': lang, 'partner_id': partner_id}
#         if partner_id:
#             lang = partner_obj.browse(cr, uid, partner_id).lang
#         context_partner = {'lang': lang, 'partner_id': partner_id}

#         if not product:
#             return {'value': {'th_weight': 0,
#                 'product_uos_qty': qty}, 'domain': {'product_uom': [],
#                    'product_uos': []}}
#         if not date_order:
#             date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

#         result = {}
#         warning_msgs = ''
#         product_obj = product_obj.browse(cr, uid, product, context=context_partner)

#         uom2 = False
#         if uom:
#             uom2 = product_uom_obj.browse(cr, uid, uom)
#             if product_obj.uom_id.category_id.id != uom2.category_id.id:
#                 uom = False
#         if uos:
#             if product_obj.uos_id:
#                 uos2 = product_uom_obj.browse(cr, uid, uos)
#                 if product_obj.uos_id.category_id.id != uos2.category_id.id:
#                     uos = False
#             else:
#                 uos = False
#         fpos = fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position) or False
#         if update_tax: #The quantity only have changed
#             result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_obj.taxes_id)

#         if not flag:
#             result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]
#             if product_obj.description_sale:
#                 result['name'] += '\n'+product_obj.description_sale
#         domain = {}
#         if (not uom) and (not uos):
#             result['product_uom'] = product_obj.uom_id.id
#             if product_obj.uos_id:
#                 result['product_uos'] = product_obj.uos_id.id
#                 result['product_uos_qty'] = qty * product_obj.uos_coeff
#                 uos_category_id = product_obj.uos_id.category_id.id
#             else:
#                 result['product_uos'] = False
#                 result['product_uos_qty'] = qty
#                 uos_category_id = False
#             result['th_weight'] = qty * product_obj.weight
#             domain = {'product_uom':
#                         [('category_id', '=', product_obj.uom_id.category_id.id)],
#                         'product_uos':
#                         [('category_id', '=', uos_category_id)]}
#         elif uos and not uom: # only happens if uom is False
#             result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
#             result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
#             result['th_weight'] = result['product_uom_qty'] * product_obj.weight
#         elif uom: # whether uos is set or not
#             default_uom = product_obj.uom_id and product_obj.uom_id.id
#             q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
#             if product_obj.uos_id:
#                 result['product_uos'] = product_obj.uos_id.id
#                 result['product_uos_qty'] = qty * product_obj.uos_coeff
#             else:
#                 result['product_uos'] = False
#                 result['product_uos_qty'] = qty
#             result['th_weight'] = q * product_obj.weight        # Round the quantity up

#         if not uom2:
#             uom2 = product_obj.uom_id
#         # get unit price

#         if not pricelist:
#             warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
#                     'Please set one before choosing a product.')
#             warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
#         else:
#             price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
#                     product, qty or 1.0, partner_id, {
#                         'uom': uom or result.get('product_uom'),
#                         'date': date_order,
#                         })[pricelist]
#             ##########code for take the Unit Price in the Sale Order Line####
#             product_customer_search = product_customer_obj.search(cr,uid,[('product_id','=',product)])
#             if product_customer_search:
#                 product_search_id = product_customer_search[0]
#                 customer_salesprice_search = product_customer_saleprice_obj.search(cr,uid,[('customer_saleprice_id','=',product_search_id),('customer_id','=',partner_id)])
#                 if customer_salesprice_search:
#                     for customer_salesprice_search_id in product_customer_saleprice_obj.browse(cr,uid,customer_salesprice_search):
#                         price = customer_salesprice_search_id.sales_price
#                         if price is False:
#                             warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
#                                     "You have to change either the product, the quantity or the pricelist.")

#                             warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
#                         else:
#                             price = 0.0
#                             result.update({'price_unit': price})
#                 else:
#                     price = 0.0
#                     result.update({'price_unit': price})
#             else:
#                 price = 0.0
#                 result.update({'price_unit': price})

#             #########################################################################
#         if warning_msgs:
#             warning = {
#                        'title': _('Configuration Error!'),
#                        'message' : warning_msgs
#                     }
#         return {'value': result, 'domain': domain, 'warning': warning}

    def onchange_sale_price(self,cr,uid,ids,sale_price):
        result={}
        product_customer_saleprice_obj = self.pool.get('product.customer.saleprice')
        if sale_price:
            sale_price_search = product_customer_saleprice_obj.browse(cr,uid,sale_price).sales_price
            if sale_price_search:
                result.update({'price_unit': sale_price_search})
        return {'value':result}

    
sale_order_line()

class stock_picking(osv.osv):
    _inherit='stock.picking'
    _columns={
        'move_lines': fields.one2many('stock.move', 'picking_id', 'Internal Moves', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
    }

stock_picking()

# class stock_move(osv.osv):
#     _inherit = 'stock.move'
#     _columns={
#         'invisible_products': fields.boolean('Invisible Combo Products'),
#     }

#     _defaults={
#             'invisible_products': False,
#     }

#     def action_done(self, cr, uid, ids, context=None):
#         """ Makes the move done and if all moves are done, it will finish the picking.
#         @return:
#         """
#         picking_ids = []
#         move_ids = []
#         wf_service = netsvc.LocalService("workflow")
#         if context is None:
#             context = {}

#         todo = []
#         for move in self.browse(cr, uid, ids, context=context):
#             if move.state=="draft":
#                 todo.append(move.id)
#         if todo:
#             self.action_confirm(cr, uid, todo, context=context)
#             todo = []

#         for move in self.browse(cr, uid, ids, context=context):
#             if move.state in ['done','cancel']:
#                 continue
#             move_ids.append(move.id)

#             if move.picking_id:
#                 picking_ids.append(move.picking_id.id)
#             if move.move_dest_id.id and (move.state != 'done'):
#                 # Downstream move should only be triggered if this move is the last pending upstream move
#                 other_upstream_move_ids = self.search(cr, uid, [('id','not in',move_ids),('state','not in',['done','cancel']),
#                                             ('move_dest_id','=',move.move_dest_id.id)], context=context)
#                 if not other_upstream_move_ids:
#                     self.write(cr, uid, [move.id], {'move_history_ids': [(4, move.move_dest_id.id)]})
#                     if move.move_dest_id.state in ('waiting', 'confirmed'):
#                         self.force_assign(cr, uid, [move.move_dest_id.id], context=context)
#                         if move.move_dest_id.picking_id:
#                             wf_service.trg_write(uid, 'stock.picking', move.move_dest_id.picking_id.id, cr)
#                         if move.move_dest_id.auto_validate:
#                             self.action_done(cr, uid, [move.move_dest_id.id], context=context)

#             self._update_average_price(cr, uid, move, context=context)
#             self._create_product_valuation_moves(cr, uid, move, context=context)
#             if move.state not in ('confirmed','done','assigned'):
#                 todo.append(move.id)
#             if picking_ids:
#                 move_ids = self.search(cr,uid,[('picking_id','=',picking_ids[0])])

#                product_obj.write(cr, uid, [product.id],{'standard_price': new_std_price})

#         if todo:
#             self.action_confirm(cr, uid, todo, context=context)

#         self.write(cr, uid, move_ids, {'state': 'done', 'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}, context=context)
#         for id in move_ids:
#              wf_service.trg_trigger(uid, 'stock.move', id, cr)

#         for pick_id in picking_ids:
#            wf_service.trg_write(uid, 'stock.picking', pick_id, cr)
#         return True

# stock_move()

# class stock_picking_out(osv.osv):
#     _name = "stock.picking.out"
#     _inherit = "stock.picking"
#     _table = "stock_picking"
#     _description = "Delivery Orders"
#     _columns = {
#     }

#     #-------------------------------------------------------------------------------------------
#     #Inherited the Stock Picking of the Warehouse Delivery Order for Force Availability Button
#     #--------------------------------------------------------------------------------------------
#     def force_assign(self, cr, uid, ids, *args):
#         """ Changes state of picking to available if moves are confirmed or waiting.
#         @return: True
#         """
#         move_line_ids = []
#         stock_move_obj = self.pool.get('stock.move')
#         wf_service = netsvc.LocalService("workflow")
#         for pick in self.browse(cr, uid, ids):
#             main_id = pick.id
#         move_ids = stock_move_obj.search(cr,uid,[('picking_id','=',main_id),('state','in',('confirmed','waiting'))]) 
#         self.pool.get('stock.move').force_assign(cr, uid, move_ids)
#         wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
#         return True

#     #-----------------------------------------------------------------------------------------------
#     #Inherited The Stock Picking of the Warehouse Delivery Order For the Check Availability Button
#     #------------------------------------------------------------------------------------------------
#     def action_assign(self, cr, uid, ids, *args):
#         """ Changes state of picking to available if all moves are confirmed.
#         @return: True
#         """
#         stock_move_obj = self.pool.get('stock.move')
#         wf_service = netsvc.LocalService("workflow")
#         for pick in self.browse(cr, uid, ids):
#             main_id = pick.id
#             if pick.state == 'draft':
#                 wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_confirm', cr)
#             move_ids = stock_move_obj.search(cr,uid,[('picking_id','=',main_id),('state','=','confirmed')])
#             if not move_ids:
#                 raise osv.except_osv(_('Warning!'),_('Not enough stock, unable to reserve the products.'))
#             self.pool.get('stock.move').action_assign(cr, uid, move_ids)
#         return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
