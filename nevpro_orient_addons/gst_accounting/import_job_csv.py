from datetime import date,datetime, timedelta
import csv
from calendar import monthrange
from osv import osv,fields
from datetime import date,datetime, timedelta
import time
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import curses.ascii
import datetime as dt
from dateutil.relativedelta import relativedelta
import calendar
import xmlrpclib
import re
import time
from base.res import res_partner
from datetime import datetime
import decimal_precision as dp
import os
import sys
from lxml import etree
from openerp.osv.orm import setup_modifiers
from tools.translate import _
import logging
logger = logging.getLogger('arena_log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
_logger = logging.getLogger(__name__)
class res_scheduledjobs(osv.osv):
	_inherit="res.scheduledjobs"
	_columns ={
		'new_entry':fields.boolean('New Entry'),
	}
	_defaults={
		'new_entry':False,
	}
res_scheduledjobs()
class import_job_csv(osv.osv):
	_name='import.job.csv'

	def _file_write(self, cr, uid, ids, file_name, value, context=None):
		attach = self.browse(cr, uid, ids, context=context)
		bin_value = value.decode('base64')
		fname = file_name
		upload_file_path=attach.file_name
		listOfFiles = os.listdir(upload_file_path)
		if listOfFiles:
			cmd= 'rm -rf '+ upload_file_path +'/*.csv'
			os.system(cmd)
		if not os.path.exists(upload_file_path):
			a=os.makedirs(upload_file_path)
			os.chmod(upload_file_path,0o777)
		full_path = upload_file_path+fname
		try:
			dirname = os.path.dirname(full_path)
			if not os.path.isdir(dirname):
				os.makedirs(dirname)
			open(full_path,'wb').write(bin_value)
		except IOError:
			_logger.error("_file_write writing %s",full_path)
		return full_path

	def _file_delete(self, cr, uid, ids, fname):
		count = self.search(cr, 1, [('file_url','=',fname)], count=True)
		if count <= 1:
			try:
				os.unlink(fname)
			except OSError:
				_logger.error("_file_delete could not unlink %s",fname)
			except IOError:
				# Harmless and needed for race conditions
				_logger.error("_file_delete could not unlink %s",fname)

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

	def _file_upload(self, cr, uid, ids, name, value, arg, context=None):
		if context is None:
			context = {}
		result = {}
		attach = self.browse(cr, uid, ids[0], context=context)        
		bin_size = context.get('bin_size')
		if attach.file_url:
			result[attach.id] = self._file_read(cr, uid, attach.file_url, attach.datas_fname, bin_size)
		else:
			result[attach.id] = value
		return result

	def _download_file(self, cr, uid, id, name, value, arg, context=None):
		if not value:
			return True       
		attach = self.browse(cr, uid, id, context=context)
		file_path_name = attach.file_name
		file_name = attach.datas_fname
		# print "sdassadsa",file_path_name
		# listOfFiles = os.listdir(file_path_name)
		# if listOfFiles:
		#     cmd= 'rm -rf '+ file_path_name +'/*.csv'
		#     os.system(cmd)
		empty = ''
		if context is None:
			context = {} 
		if file_name.endswith('.csv') or file_name.endswith('.CSV'):    
			fname = self._file_write(cr, uid, id, file_name, value, context=context)
			#os.chmod(fname,0o777)
		else:
			raise osv.except_osv(('Warning!'),("Wrong file is been uploaded."))
		super(import_job_csv, self).write(cr, uid, [id], {'file_url': fname,'file_upload':empty}, context=context)
		return True
	_columns={
		'name':fields.char('Name',size=100),
		'file_upload': fields.function(_file_upload, fnct_inv=_download_file, type='binary', string='File Upload', nodrop=True),
		'datas_fname': fields.char('File Name',size=256),
		'file_url':fields.char('File URL', size=256),
		'file_name':fields.char('File Name Character',size=990),
	}
	_defaults={
		'file_name':'/opt/openerp/job_transfer_csv/'
		# 'file_name':'/home/chaitalikelsukar/Desktop/Migration_Updated/SSD_Updated_New_GST/SSD_Updated_New/gst_accounting/import_job_csv/'

		}
	def update_job_csv(self,cr,uid,ids,context=None):
		o= self.browse(cr,uid,ids[0])
		folder_path = o.file_name
		listOfFiles = os.listdir(folder_path)
		file_path = folder_path+str(listOfFiles[0])
		with open(file_path, 'r') as csvfile:
			reader = csv.reader(csvfile, delimiter=',')
			count = 0
			ou_id=''
			pms_search=None
			account_id_search = False
			for row in reader:
				if count != 0:
					if row[5]:
						cr.execute("select id from product_product where name_template = '%s' limit 1"%(row[5]))
						pms_search=cr.fetchone()[0]
					if row[14] and row[14] != 'None':
						cr.execute("select ou_id from res_partner where id= %s"%(row[14]))
						ou_id=cr.fetchone()[0]
					cr.execute("select id from res_scheduledjobs where id=%s"%(row[11]))
					if_exists=cr.fetchone()
					assigned_technician = row[12] if str(row[12]).strip()!= 'None' else 'NULL'
					sale_contract = row[13] if str(row[13]).strip() !='None' else 'Null'
					name_contact=row[14] if str(row[14]).strip() != 'None' else 'Null'
					location_id2=row[15] if str(row[15]).strip()!= 'None' else 'Null'
					if if_exists:
						cr.execute("update res_scheduledjobs set job_start_time ='%s',new_job_end_time1='%s',assigned_technician = %s,pms_search='%s',location_id2=%s where id =%s"%(row[3],row[4],assigned_technician,pms_search,location_id2,row[11]))
						cr.commit()
					else:
						cr.execute("insert into res_scheduledjobs (job_start_time,new_job_end_time1,assigned_technician,pms_search,location_id2,id,sale_contract,job_id,name_contact,scheduled_job_id,customer_id,new_entry,pms,job_end_time,technician_squad_merge) values ('%s','%s',%s,%s,%s,%s,%s,'%s',%s,'%s','%s',True,'%s','%s','%s')"%(row[3],row[4],assigned_technician,pms_search,location_id2,row[11],sale_contract,row[2],name_contact,row[1],str(ou_id),row[5],row[4],row[6]))
						cr.commit()
				count += 1
		return {'type': 'ir.actions.act_window_close'}
import_job_csv()
