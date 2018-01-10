from openerp.osv import osv,fields
import os
import time
import base64
import datetime
import dateutil.relativedelta as relativedelta
import logging
import lxml
import urlparse

import openerp
from openerp import SUPERUSER_ID
from openerp.osv import osv, fields
from openerp import tools, api
from openerp.tools.translate import _
from urllib import urlencode, quote as quote

class jasper_cron(osv.osv):
    _name = 'jasper.cron'

    def compose_mail(self, cr, uid, ids, context=None):
        att_obj = self.pool.get('ir.attachment')
        template_obj = self.pool.get('email.template')
        model_obj = self.pool.get('ir.model')
        mail_mail = self.pool.get('mail.mail')
        base_config = self.pool.get('base.config.settings')
        model_ids = model_obj.search(cr, uid, [('model','=','jasper.cron')])
       	template_id = template_obj.search(cr, uid, [('model_id','=',model_ids[0])])
        if context is None:
            context = {}
        listOfFiles = False
        att_ids = []
        msg_id = False
        html_data = ''
        res_id = None
        raise_exception = False
        path_search = cr.execute("select jasper_file_path from base_config_settings order by id desc limit 1")
        path_ids = cr.fetchall()
        if path_ids:
            fullpath = path_ids[0][0]
            if not fullpath:
                fullpath = ''
        else:
            fullpath = ''
        try:
            listOfFiles = os.listdir(fullpath)
        except IOError:
            _logger.error("Directory Path could not be found: %s",full_path)
        
        if listOfFiles and template_id:
            values = template_obj.generate_email(cr, uid, template_id[0], res_id, context=context)
            print "valuesssssss", values
            attachment_ids = values.pop('attachment_ids', [])
            attachments = values.pop('attachments', [])
            msg_id = mail_mail.create(cr, uid, values, context=context)
            mail = mail_mail.browse(cr, uid, msg_id, context=context)
            for f in listOfFiles:
                if f.endswith('html'):
                    html_file = fullpath + '/' + f
                    html_data = open(html_file,'rb').read()
                else:
                    pdf_file = fullpath + '/' + f
                    att_id = att_obj.create(cr, uid, {'name':"jasper_dsp_%s"%(time.strftime('%Y-%m-%d %H:%M:%S')),
                    						'type':'binary',
                    						'datas':open(pdf_file,'rb').read().encode('base64'),
                    						'res_model': 'mail.message',
                    						'res_id': mail.mail_message_id.id,
                    						'datas_fname':f})
                    att_ids.append(att_id)
            values['attachment_ids'] = [(6, 0, att_ids)]
            body_html = mail_mail.browse(cr, uid, msg_id).body_html
            mail_mail.write(cr, uid, msg_id, {'attachment_ids': [(6, 0, att_ids)],
                                            'body_html':str(body_html) + str(html_data)}, context=context)
            mail_mail.send(cr, uid, [msg_id], raise_exception=raise_exception, context=context)
            
            for f in listOfFiles:
                for att_data in att_obj.browse(cr, uid, att_ids):
                    if f == att_data.datas_fname:
                        file_path = fullpath + '/' + f
                        att_obj.write(cr, uid, [att_data.id], {'url':file_path,'db_datas':False,'type':'url','datas':False})                    
        return msg_id

    def send_mail(self,cr,uid,context=None):
        ids=self.search(cr,uid,[],context=None)
        value=self.compose_mail(cr,uid,ids,context=context)
        return value

jasper_cron()

class base_config_settings(osv.osv):
    _inherit = 'base.config.settings'

    _columns = {
                'jasper_file_path':fields.char('Japser File Path')
    }
base_config_settings()

class email_template(osv.osv):
    _inherit = 'email.template'

    _columns = {                
                'user_ids':fields.many2many('res.users','email_template_user_rel','tmpl_id','user_id','To (Users)'),
                'department_ids':fields.many2many('hr.department','email_template_dept_rel','tmpl_id','dept_id','To (Department)')
    }

    def generate_recipients_batch(self, cr, uid, results, template_id, res_ids, context=None):
        """Generates the recipients of the template. Default values can ben generated
        instead of the template values if requested by template or context.
        Emails (email_to, email_cc) can be transformed into partners if requested
        in the context. """
        if context is None:
            context = {}
        template = self.browse(cr, uid, template_id, context=context)

        if template.use_default_to or context.get('tpl_force_default_to'):
            ctx = dict(context, thread_model=template.model)
            default_recipients = self.pool['mail.thread'].message_get_default_recipients(cr, uid, res_ids, context=ctx)
            for res_id, recipients in default_recipients.iteritems():
                results[res_id].pop('partner_to', None)
                results[res_id].update(recipients)

        for res_id, values in results.iteritems():
            partner_ids = values.get('partner_ids', list())
            email_to = values.get('email_to', str())
            if context and context.get('tpl_partners_only'):
                mails = tools.email_split(values.pop('email_to', '')) + tools.email_split(values.pop('email_cc', ''))
                for mail in mails:
                    partner_id = self.pool.get('res.partner').find_or_create(cr, uid, mail, context=context)
                    partner_ids.append(partner_id)
            partner_to = values.pop('partner_to', '')
            if partner_to:
                # placeholders could generate '', 3, 2 due to some empty field values
                tpl_partner_ids = [int(pid) for pid in partner_to.split(',') if pid]
                partner_ids += self.pool['res.partner'].exists(cr, SUPERUSER_ID, tpl_partner_ids, context=context)
            user_ids = template.user_ids
            if user_ids:
                for user in user_ids:
                    partner_ids += [int(user.partner_id.id)]
                    email_to += str('%s,'%(user.partner_id.email))
                email_to = email_to[:-1]
            department_ids = template.department_ids
            if department_ids:
                for department in department_ids:
                    for hr in department.member_ids:
                        partner_ids += [int(hr.user_id.partner_id.id)]
                        email_to += str('%s,'%(hr.user_id.partner_id.email))
                email_to = email_to[:-1]
            results[res_id]['partner_ids'] = partner_ids
            results[res_id]['email_to'] = email_to
        return results