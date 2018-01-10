# -*- coding: utf-8 -*-

import math

from osv import fields,osv
import tools
import pooler
from tools.translate import _
from openerp import SUPERUSER_ID
import re
import time

class res_company(osv.osv):
    _inherit = 'res.company'
    
    _columns = {
        'logo_header': fields.binary("Image Header", help="This field holds the image used for report\'s header"),
    }
    
res_company()

class res_users(osv.osv):
    _inherit = 'res.users'
    
    def _get_job(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for p in self.browse(cr, uid, ids, context=context):
            res[p.id] = p.employee_ids[0].job_id.name
        return res
    
    _columns = {
        'login_date': fields.datetime('Latest connection', select=1),
        'job': fields.function(_get_job, string='Job Title', type='char'), #TODO optimization store etc
        #related('employee_ids', 'job_id', type='one2many', string='Job Title', readonly=1),
    }
    
    def change_password(self, cr, uid, old_passwd, new_passwd, context=None):
        
        """Change current user password. Old password must be provided explicitly
        to prevent hijacking an existing user session, or for cases where the cleartext
        password is not used to authenticate requests.

        :return: True if OK
        :return: "too short" if password is too short
        :return: "no numbers" if password has no numbers
        :return: "no letters" if password has no letters
        :raise: openerp.exceptions.AccessDenied when old password is wrong
        :raise: except_osv when new password is not set or empty
        """
        
        self.check(cr.dbname, uid, old_passwd)
        if new_passwd:
            
            # CHECK PASSWORD
            if len(new_passwd) < 8:
                #raise osv.except_osv(_('Warning!'), _("Password must be at least 8 characters long."))
                return "too short"
            
            if not re.search('\d+',new_passwd):
                #raise osv.except_osv(_('Warning!'), _("Password must have numbers."))
                return "no numbers"
            
            if not (re.search('[a-z]+',new_passwd) or re.search('[A-Z]+',new_passwd)):
                #raise osv.except_osv(_('Warning!'), _("Password must have letters."))
                return "no letters"

            return self.write(cr, uid, uid, {'password': new_passwd})
        raise osv.except_osv(_('Warning!'), _("Setting empty passwords is not allowed for security reasons!"))
    
res_users()

class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    _order = "ref,name"
    
    _columns = {
        'vendor_number': fields.char('Zeeva vendor number',size=64, help="Zeeva vendor number in this partner."),
        'supplier_rating': fields.selection([('1','Tier 1'),('2','Tier 2'),('3','Tier 3')], 'Zeeva supplier rating'),
        'department': fields.selection([('sales','Sales'), ('artwork','Artwork'), ('shipping','Shipping'), ('finance','Finance')], 'Department'),
        'is_sub_company': fields.boolean('Is a Sub-company'),
        'subcompany_name': fields.char('Subcompany Name', size=128),
        'prod_categ_ids': fields.many2many('product.category', 'res_partner_product_category_rel', 'partner_id', 'product_category_id', 'Product categories'),

        # predef fields for orders
        'port_of_discharge': fields.many2one('stock.port', 'Port of Discharge'),
        'port_of_loading': fields.many2one('stock.port', 'Port of Loading'),
        'incoterm': fields.many2one('stock.incoterms', 'Incoterm', help="International Commercial Terms are a series of predefined commercial terms used in international transactions."),
        #'payment_term': fields.many2one('account.payment.term', 'Payment Term'),
        
        #'template_ids': fields.one2many('task.template', 'customer_id', 'Templates'),
        
        'creation_user': fields.many2one('res.users','Created by'),
        'creation_date': fields.date('Created on'),
        
        'input_status': fields.selection([
            ('draft','Draft'),
            ('modif','Modification'),
            ('submited','Submitted'),
            ('approved','Approved')],
            'Input status', track_visibility='onchange'),
    }
    
    _defaults = {
        'is_company': False,
        'user_id': lambda obj, cr, uid, context: uid,
        'date': fields.date.context_today,
        'ref': '/',
        'opt_out': True,
        'input_status': 'draft',
    }
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            if record.parent_id and not record.is_company:
                if record.is_sub_company:
                   name =  "%s [%s]" % (name, record.subcompany_name)
                else:
                    name =  "%s [%s]" % (name, record.parent_id.name)
            if context.get('show_address'):
                name = name + "\n" + self._display_address(cr, uid, record, without_company=True, context=context)
                name = name.replace('\n\n','\n')
                name = name.replace('\n\n','\n')
            if context.get('show_email') and record.email:
                name = "%s <%s>" % (name, record.email)
            res.append((record.id, name))
        return res
    
    def create(self, cr, user, vals, context=None):
        
        if ('is_company' in vals) and vals['is_company'] and (('ref' not in vals) or (vals.get('ref')=='/')):
            tmp = "" #format is CCNNN0
            code= ""
            
            if ('customer' in vals) and (vals.get('customer')==True):
                #2letters for country code
                if vals['country_id']:
                    country_obj = self.pool.get('res.country').browse(cr, user, vals['country_id'], context=None)
                    tmp += country_obj.code
                else:
                    tmp += "--"
                
                #3letters for the begining of the customer name
                if vals['name']:
                    tmp += vals['name'].replace(" ", "")[0:3].upper()
                else:
                    tmp += "---"
                
                #1digit to avoid double
                partner_pool = self.pool.get('res.partner')
                for i in range(1,1000):
                    code = tmp + str(i)
                    partner_object = partner_pool.search(cr, user, [('ref', '=', code)])
                    
                    if not partner_object:
                        break
                    
                    #print "searchID: ", partner_pool.browse(cr,user,partner_object[0]).id
                    #print "IDS: ", ids
                        
                    #if partner_pool.browse(cr,user,partner_object[0]).id in ids:
                        #break
                    
                vals['ref'] = code
            
            else:
                tmp = "SUP"
                
                #3digits to avoid double
                partner_pool = self.pool.get('res.partner')
                for i in range(1,10000):
                    code = tmp + "%03d" % i
                    partner_object = partner_pool.search(cr, user, [('ref', '=', code)])
                    
                    if not partner_object:
                        break
                        
                    #if partner_pool.browse(cr,user,partner_object[0]).id in ids:
                        #break
                        
                vals['ref'] = code
        
        else:
            vals['ref'] = ''
        
        vals['creation_user'] = user
        vals['creation_date'] = fields.date.context_today(self,cr,user,context=context)

        return super(res_partner,self).create(cr, user, vals, context)
    
    
    # Customer input temp approval
    def input_request(self, cr, uid, ids, context=None):
        for customer in self.browse(cr, uid, ids):
            
            # ADD bosses
            boss_ids = self.pool.get('res.users').search(cr, uid, ['|','|',('login','=','nitin'),('login','=','akshay'),('login','=','admin')])
            if boss_ids:
                self.message_subscribe_users(cr, uid, [customer.id], user_ids=boss_ids)
            
            # Send request for approval
            #message = _("<b>Approval requested</b> for new customer %s") % (customer.name)
            #print [m.id for m in customer.message_follower_ids]
            #self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)
            
        return self.write(cr, uid, ids, {'input_status': 'submited'}, context=context)
    
    def input_modif(self, cr, uid, ids, context=None):
                
        return self.write(cr, uid, ids, {'input_status': 'modif'}, context=context)
        
    def input_approval(self, cr, uid, ids, context=None):
        for customer in self.browse(cr, uid, ids):
            
            # ADD the salesman
            if customer.user_id:
                self.message_subscribe_users(cr, uid, [customer.id], user_ids=[customer.user_id.id])
                
        return self.write(cr, uid, ids, {'input_status': 'approved'}, context=context)
        
    #def message_get_suggested_recipients(self, cr, uid, ids, context=None):
        #recipients = super(res_partner, self).message_get_suggested_recipients(cr, uid, ids, context=context)
        #print recipients
        ##for partner in self.browse(cr, uid, ids, context=context):
            ##self._message_add_suggested_recipient(cr, uid, recipients, partner, partner=partner, reason=_('Partner Profile'))
        #return recipients
    
    # OVERWRITE of the function to avoid sending wrong emails to customers & suppliers
    def message_get_suggested_recipients(self, cr, uid, ids, context=None):
        """ Returns suggested recipients for ids. Those are a list of
            tuple (partner_id, partner_name, reason), to be managed by Chatter. """
        result = dict.fromkeys(ids, list())
        if self._all_columns.get('user_id'):
            for obj in self.browse(cr, SUPERUSER_ID, ids, context=context):  # SUPERUSER because of a read on res.users that would crash otherwise
                if not obj.user_id or not obj.user_id.partner_id:
                    continue
                #self._message_add_suggested_recipient(cr, uid, result, obj, partner=obj.user_id.partner_id, reason=self._all_columns['user_id'].column.string, context=context)
        return result
    
    
    # OVERWRITE of the function to allow messages for partners as a thread #TODO doesn't work
    #def message_post(self, cr, uid, thread_id, **kwargs):
        #""" Override related to res.partner. In case of email message, set it as
            #private:
            #- add the target partner in the message partner_ids
            #- set thread_id as None, because this will trigger the 'private'
                #aspect of the message (model=False, res_id=False)
        #"""
        #print thread_id
        #print kwargs
        #print kwargs['context']['default_res_id']
        #mail_message = self.pool.get('mail.message')
        #message_ids = mail_message.search(cr, SUPERUSER_ID, [('id', '=', thread_id)], context=None)
        #print message_ids
        
        #if isinstance(thread_id, (list, tuple)):
            #thread_id = thread_id[0]
        #if kwargs.get('type') == 'email':
            #partner_ids = kwargs.get('partner_ids', [])
            #if thread_id not in [command[1] for command in partner_ids]:
                #partner_ids.append((4, thread_id))
            #kwargs['partner_ids'] = partner_ids
            #thread_id = False
        #return super(res_partner, self).message_post(cr, uid, thread_id, **kwargs)
    
    #ONCHANGE to remove
    def onchange_ref(self, cr, uid, ids, name, country, customer, context=None):
        result = {}
        tmp = "" #format is CCNNN0
        code= ""
        
        if customer:
            #2letters for country code
            if country:
                country_obj = self.pool.get('res.country').browse(cr, uid, country, context=None)
                tmp += country_obj.code
            else:
                tmp += "--"
            
            #3letters for the begining of the customer name
            if name:
                tmp += name[0:3].upper()
            else:
                tmp += "---"
            
            #1digit to avoid double
            partner_pool = self.pool.get('res.partner')
            for i in range(1,1000):
                code = tmp + str(i)
                partner_object = partner_pool.search(cr, uid, [('ref', '=', code)])
                
                if not partner_object:
                    break
                
                #print "searchID: ", partner_pool.browse(cr,uid,partner_object[0]).id
                #print "IDS: ", ids
                    
                if partner_pool.browse(cr,uid,partner_object[0]).id in ids:
                    break
                
            result = {'value': {'ref': code}}
        
        else:
            tmp = "SUP"
            
            #3digits to avoid double
            partner_pool = self.pool.get('res.partner')
            for i in range(1,10000):
                code = tmp + "%03d" % i
                partner_object = partner_pool.search(cr, uid, [('ref', '=', code)])
                
                if not partner_object:
                    break
                    
                if partner_pool.browse(cr,uid,partner_object[0]).id in ids:
                    break
                
            result = {'value': {'ref': code}}
        
        return result
        
    def onchange_email(self, cr, uid, ids, email, context=None):
        context = context or {}
        warning = {}
        
        if not email:
            return {}
        
        if not tools.email_split(email):
            warning = {
                'title': _('Email Format Warning!'),
                'message' : _('The email is not well formatted, it should be johndoe@example.com')
            }
            
        return {'warning': warning,}
        
    def _display_address(self, cr, uid, address, without_company=False, context=None):

        '''
        The purpose of this function is to build and return an address formatted accordingly to the
        standards of the country where it belongs.

        :param address: browse record of the res.partner to format
        :returns: the address formatted in a display that fit its country habits (or the default ones
            if not country is specified)
        :rtype: string
        '''

        # get the information that will be injected into the display format
        # get the address format
        address_format = address.country_id and address.country_id.address_format or \
              "%(street)s\n%(street2)s\n%(city)s %(state_code)s %(zip)s\n%(country_name)s"
        args = {
            'state_code': address.state_id and address.state_id.code or '',
            'state_name': address.state_id and address.state_id.name or '',
            'country_code': address.country_id and address.country_id.code or '',
            'country_name': address.country_id and address.country_id.name or '',
            #'company_name': address.parent_id and address.parent_id.name or '',
        }
        for field in self._address_fields(cr, uid, context=context):
            args[field] = getattr(address, field) or ''
        #if without_company:
            #args['company_name'] = ''
        #elif address.parent_id:
            #address_format = '%(company_name)s\n' + address_format
        return address_format % args
        
    
res_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
