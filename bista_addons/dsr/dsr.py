from openerp import SUPERUSER_ID
from openerp.osv import osv,fields
from openerp.tools.translate import _
from stdnum import imei
import datetime
from datetime import date, timedelta
import time
import re
import logging
import pytz
import calendar
from dateutil.relativedelta import relativedelta
from openerp.addons.jasper_integration import jasper
from openerp import api

logger = logging.getLogger('arena_log')
#_logger = logging.getLogger(__name__)
############## Transaction Type ##############
_prod_type = [('postpaid','Postpaid'),('prepaid','Prepaid'),('feature','Data Feature'),('upgrade','Upgrade'),('accessory','Accessory')]
_tracker_str_type = [('hm','Home/Base Store'),('cv','Covering_store')]


############## EMail Validation ################
def email_match(email):
    if email and not re.match("[^@]+@[^@]+\.[^@]+", email):
        raise osv.except_osv(_('Error !'),_("Please enter correct email address."))
    return True

############# Account Phone Validation #################
def acc_phone_check(phone):
    if phone:
        if not re.match("^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$", phone):
            raise osv.except_osv(_('Error !'),_("Account Mobile # %s is not valid."%(phone)))
        else:
            count = 0
            nums = str(phone)
            length = len(phone)
            for num in nums:
                if nums[0] == num:
                    count = count + 1;
            if count == length:
                raise osv.except_osv(_('Error !'),_("Account Mobile # %s is not valid."%(phone)))
    return True

############# Phone Validation #################
def phone_check(phone):
    if phone:
        if not re.match("^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$", phone):
            raise osv.except_osv(_('Error !'),_("Mobile Phone %s is not valid."%(phone)))
        else:
            count = 0
            nums = str(phone)
            length = len(phone)
            for num in nums:
                if nums[0] == num:
                    count = count + 1;
            if count == length:
                raise osv.except_osv(_('Error !'),_("Mobile Phone %s is not valid."%(phone)))  
    return True

############# Validate CIHU, JUMP, Reliance Ticket # ############
#def validate_cihu(cihu_no):
#    if cihu_no == '111111111':
#        return True
#    if cihu_no and not re.match('^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{3})$', cihu_no):
#        raise osv.except_osv(_('Error !'),_("Order # is not valid."))
#    return True

def validate_cihu(cihu_no):
    if (cihu_no == '111111111') or (cihu_no == '123456789'):
        raise osv.except_osv(_('Error !'),_("CIHU # %s is not valid."%(cihu_no)))
    if cihu_no and not re.match('^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{3})$', cihu_no):
        raise osv.except_osv(_('Error !'),_("CIHU # %s is not valid."%(cihu_no)))
    return True

############ IMEI Number Validation ###############
def imei_check(number):
    if number:
        if not imei.is_valid(number):
            raise osv.except_osv(_('Error !'),_("IMEI number %s is not valid."%(number)))
        else:
            count = 0
            nums = str(number)
            length = len(number)
            for num in nums:
                if nums[0] == num:
                    count = count + 1;
            if count == length:
                raise osv.except_osv(_('Error !'),_("IMEI number %s is not valid."%(number)))
            if length < 15:
                raise osv.except_osv(_('Error !'),_("IMEI number %s should be 15 digit."%(number)))
    return True

############ IMEI Number Prepaid Validation ###############
def imei_check_prepaid(number):
    # if number == '111111111111111':
    #     return True
    if number:
        if not imei.is_valid(number):
            raise osv.except_osv(_('Error !'),_("IMEI number %s is not valid."%(number)))
        else:
            count = 0
            nums = str(number)
            length = len(number)
            for num in nums:
                if nums[0] == num:
                    count = count + 1;
            if count == length:
                raise osv.except_osv(_('Error !'),_("IMEI Phone %s is not valid."%(number)))
            if length < 15:
                raise osv.except_osv(_('Error !'),_("IMEI number %s should be 15 digit."%(number)))
    return True

############ Temporary Number Validation ###########
def temp_check(phone):
    if phone:
        if not re.match("^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$", phone):
            raise osv.except_osv(_('Error !'),_("Temporary # %s is not valid."%(phone)))
        else:
            count = 0
            nums = str(phone)
            length = len(phone)
            for num in nums:
                if nums[0] == num:
                    count = count + 1;
            if count == length:
                raise osv.except_osv(_('Error !'),_("Temporary Mobile # %s is not valid."%(phone)))
    return True


########### SIM Number Validation #####################
def luhn_checksum(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d*2))
    return checksum % 10
 
def is_luhn_valid(card_number):
    return luhn_checksum(card_number) == 0

def sim_validation(card_number):
    card_number = card_number.strip()
    if card_number:
        count = 0
        nums = str(card_number)
        length = len(card_number)
        for num in nums:
            if nums[0] == num:
                count = count + 1;
        if count == length:
            raise osv.except_osv(_('Error !'),_("SIM number %s is not valid."%(card_number))) 
    if not card_number.isdigit():
        raise osv.except_osv(_('Error !'),_("SIM number %s should have Integers only."%(card_number)))
    if not re.match(r'\d', card_number):
        raise osv.except_osv(_('Error !'),_("SIM number %s is not valid."%(card_number)))
    if card_number and not is_luhn_valid(card_number):
        raise osv.except_osv(_('Error !'),_("SIM number %s is not valid."%(card_number)))
    return True

class product_code_type_update(osv.osv):
    _name = 'product.code.type.update'
    _columns = {
                'start_date':fields.date('Start Date', required="1"),
                'end_date':fields.date('End Date', required="1")
    }
    
    def update_dsr_code_type(self, cr, uid, ids, context=None):
        dsr_obj = self.pool.get('wireless.dsr')
        prod_obj = self.pool.get('product.product')
        self_data = self.browse(cr, uid, ids[0])
        prod_data = prod_obj.browse(cr, uid, context.get('active_id'))
        start_date = self_data.start_date
        end_date = self_data.end_date
        dsr_ids = dsr_obj.search(cr, uid, [('dsr_date','>=',start_date),('dsr_date','<=',end_date)])
        if dsr_ids and prod_data:
            prod_code_type = prod_data.dsr_prod_code_type.id
            prod_id = prod_data.id
            if len(dsr_ids) > 1:
                cond = "in %s"%(tuple(dsr_ids),)
            else:
                cond = "= %s"%(dsr_ids[0])
            cr.execute("update wireless_dsr_postpaid_line set dsr_product_code_type=%s where dsr_product_code=%s and product_id "%(prod_code_type,prod_id)+cond+"")
            cr.execute("update wireless_dsr_upgrade_line set dsr_product_code_type=%s where dsr_product_code=%s and product_id "%(prod_code_type,prod_id)+cond+"")
            cr.execute("update wireless_dsr_prepaid_line set dsr_product_code_type=%s where dsr_product_description=%s and product_id "%(prod_code_type,prod_id)+cond+"")
            cr.execute("update wireless_dsr_feature_line set dsr_product_code_type=%s where dsr_product_code=%s and feature_product_id "%(prod_code_type,prod_id)+cond+"")
            log_vals = {
                        'start_date':start_date,
                        'end_date':end_date,
                        'prod_id':prod_id,
                        'prod_code_type':prod_code_type,
                        'user_id':uid
            }
            self.pool.get('product.code.type.update.log').create(cr, uid, log_vals)
        return True

    def create(self, cr, uid, vals, context=None):
        log_vals = {}
        prod_obj = self.pool.get('product.product')
        start_date = vals['start_date']
        end_date = vals['end_date']
        if start_date > end_date:
            raise osv.except_osv(('Warning!!'),('Start date cannot greater than end date.'))
        res = super(product_code_type_update, self).create(cr, uid, vals, context=context)
        return res

product_code_type_update()

class product_code_type_update_log(osv.osv):
    _name = 'product.code.type.update.log'
    _columns = {
                'user_id':fields.many2one('res.users','User'),
                'start_date':fields.date('Entry Start Date'),
                'end_date':fields.date('Entry End Date'),
                'prod_id':fields.many2one('product.product', 'Product'),
                'prod_code_type':fields.many2one('product.category','Product Code Type')
    }
product_code_type_update_log()

########### Inherited Product Class ################
class product_product(osv.osv):
    _inherit = 'product.product'

    _columns = {
                'monthly_access':fields.float('Monthly Access(monthly rate customer getting billed)'),
                'contract_term':fields.integer('Contract Term(Plan months)'),
                'dsr_sku':fields.char('SKU #', size=24),
                'dsr_categ_id':fields.selection(_prod_type, 'Transaction Type'),
#                'dsr_product_sub_categ_id':fields.many2one('product.category', "Product Code type"),
                'dsr_second_categ':fields.many2one('product.category', 'Secondary Category'),
                'dsr_prod_code_type':fields.many2one('product.category', 'Product Code Type'),
                'dsr_prod_type':fields.many2one('product.category', 'Product Type'),
                'is_intl':fields.boolean('Intl Talk & Text'),
                'is_tether':fields.boolean('Tether'),
                'is_php':fields.boolean('PHP'),
                'is_jump':fields.boolean('JUMP'),
                'is_data':fields.boolean('Data'),
                'is_msg':fields.boolean('Messaging'),
                'is_other':fields.boolean('Other'),
                'non_comm':fields.boolean('Non Commissionable'),
                'sequence':fields.integer('Priority Sequence'),
                'is_mob_internet':fields.boolean('Mobile Internet'),
                'is_scnc':fields.boolean('SCNC'),
                'is_simple_starter':fields.boolean('Simple Starter'),
                'is_voice_barred':fields.boolean('Voice Barred'),
                'is_score':fields.boolean('SCORE'),
                'transaction_line_rel':fields.one2many('transaction.line.soc.rel','soc_code','Transaction Line Association')
#                'attach_data_multi':fields.many2many('product.product','prod_data_multi_rel','parent_id','child_id','Attachable Data SOC')
        }
    _rec_name = 'default_code'
    _order = 'sequence'    
    _sql_constraints = [
                ('soc_code_name_uniq', 'unique(default_code,dsr_prod_type)', 'SOC Code and Product Type combination must be unique!'),
    ]

    def onchange_prod_type(self, cr, uid, ids, categ_id):
        if categ_id:
            return {'value': {'dsr_prod_type':categ_id,
                            'dsr_prod_code_type':False}}
        return {'value': {'dsr_prod_type':False,
                        'dsr_prod_code_type':False}}

#***************************************version8*****************************
    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []

        def _name_get(d):
            name = d.get('name','')
            code = context.get('display_default_code', True) and d.get('default_code',False) or False
            # trans_type = d.get('dsr_categ_id', False)
            #context doesn't have dsr_categ_id
            trans_type = self.browse(cr,user,d.get('id')).dsr_categ_id or False
            if "trans_type" == 'prepaid' and name:
                name = '%s' % (name)
            elif trans_type != 'prepaid' and code:
                name = '%s' % (code)
            # if code:
            #     name = '[%s] %s' % (code,name)

            return (d['id'], name)

        partner_id = context.get('partner_id', False)
        if partner_id:
            partner_ids = [partner_id, self.pool['res.partner'].browse(cr, user, partner_id, context=context).commercial_partner_id.id]
        else:
            partner_ids = []
        # all user don't have access to seller and partner
        # check access and use superuser
        self.check_access_rights(cr, user, "read")
        self.check_access_rule(cr, user, ids, "read", context=context)
        result = []
#        for product in self.browse(cr, SUPERUSER_ID, ids, context=context):
        for product in self.browse(cr, user, ids, context=context):
            variant = ", ".join([v.name for v in product.attribute_value_ids])
            name = variant and "%s (%s)" % (product.name, variant) or product.name
            sellers = []
            if partner_ids:
                sellers = filter(lambda x: x.name.id in partner_ids, product.seller_ids)
            if sellers:
                for s in sellers:
                    seller_variant = s.product_name and "%s (%s)" % (s.product_name, variant) or False
                    mydict = {
                              'id': product.id,
                              'name': seller_variant or name,
                              'default_code': s.product_code or product.default_code,
                              }
                    result.append(_name_get(mydict))
            else:
                mydict = {
                          'id': product.id,
                          'name': name,
                          'default_code': product.default_code,
                          }
                result.append(_name_get(mydict))
        return result

    def create(self, cr, uid, vals, context=None):
        prod_rule = self.pool.get('product.business.rule')
        res = super(product_product, self).create(cr, uid, vals)
        is_scnc = vals.get('is_scnc')
        is_mob_internet = vals.get('is_mob_internet')
        is_voice = vals.get('is_voice_barred')
        if vals.has_key('dsr_categ_id') and vals['dsr_categ_id']:
            dsr_categ_id = vals['dsr_categ_id']
            if dsr_categ_id == 'postpaid':
                if is_mob_internet or is_voice:
                    return res
                elif is_scnc:
                    for data_id in self.search(cr, uid, [('is_data','=',True),('is_scnc','=',True)]):
                        prod_rule.create(cr, uid, {'main_soc_id':res,'data_soc_id':data_id})
                else:
                    for data_id in self.search(cr, uid, [('is_data','=',True)]):
                        prod_rule.create(cr, uid, {'main_soc_id':res,'data_soc_id':data_id})
        return res

    def write(self, cr, uid, ids, vals, context=None):
        prod_rule = self.pool.get('product.business.rule')
        res = super(product_product, self).write(cr, uid, ids, vals)
        for id in ids:
            self_data = self.browse(cr, uid, id)
            if vals.has_key('dsr_categ_id') and vals['dsr_categ_id']:
                dsr_categ_id = vals['dsr_categ_id']
            else:
                dsr_categ_id = self_data.dsr_categ_id
            if vals.has_key('is_scnc') and vals['is_scnc']:
                is_scnc = vals['is_scnc']
            else:
                is_scnc = self_data.is_scnc
            if vals.has_key('is_mob_internet') and vals['is_mob_internet']:
                is_mob_internet = vals['is_mob_internet']
            else:
                is_mob_internet = self_data.is_mob_internet
            if vals.has_key('is_voice_barred') and vals['is_voice_barred']:
                is_voice = vals['is_voice_barred']
            else:
                is_voice = self_data.is_voice_barred
            prod_rule_ids = prod_rule.search(cr, uid, [('main_soc_id','=',id)])
            if dsr_categ_id == 'postpaid':
                if prod_rule_ids:
                    prod_rule.write(cr, uid, prod_rule_ids, {'active':False})
                if is_mob_internet or is_voice:
                    continue
                elif is_scnc:
                    for data_id in self.search(cr, uid, [('is_data','=',True),('is_scnc','=',True)]):
                        prod_rule.create(cr, uid, {'main_soc_id':id,'data_soc_id':data_id})
                else:
                    for data_id in self.search(cr, uid, [('is_data','=',True)]):
                        prod_rule.create(cr, uid, {'main_soc_id':id,'data_soc_id':data_id})
            else:
                prod_rule.write(cr, uid, prod_rule_ids, {'active':False})
        return res

    def unlink(self, cr, uid, ids, context=None):
        prod_rule = self.pool.get('product.business.rule')
        for id in ids:
            prod_rule_ids = prod_rule.search(cr, uid, [('main_soc_id','=',id)])
            prod_rule.unlink(cr, uid, prod_rule_ids)
        res = super(product_product, self).unlink(cr, uid, ids)
        return res

product_product()

############## Product Category Inherited Class ###################
class product_category(osv.osv):
    _inherit = 'product.category'
    _columns = {
                'prod_type':fields.selection(_prod_type, 'Transaction Type'),
                'sequence':fields.integer('Sequence'),
                'inactive':fields.boolean('Inactive'),
    }
    _order = 'sequence'
    _defaults = {
                'inactive':False
    }

product_category()

class product_subcategory(osv.osv):
    _name = 'product.subcategory'
    _description = "Product Code Type"
    _columns = {
                'name' :fields.char('Product Code Type'),
                'prod_type':fields.many2one('product.category', 'Product Type'),
    }
product_subcategory()

class product_business_rule(osv.osv):
    _name = 'product.business.rule'
    _columns = {
                'main_soc_id':fields.many2one('product.product','Postpaid/Upgrade SOC Code',domain="[('dsr_categ_id','=','postpaid')]"),
                'data_soc_id':fields.many2one('product.product','Data SOC Code',domain="[('is_data','=',True)]"),
                'active':fields.boolean('Active')
    }
    _defaults = {
                'active':True
    }
product_business_rule()

################## TAC Code Master ###############################
class tac_code_master(osv.osv):
    _name = 'tac.code.master'
    _description = "TAC Code Master"
    _columns = {
                'phone_model':fields.many2one('phone.model.master', 'Phone Model'),
                'phone_type':fields.many2one('phone.type.master', 'Phone Type'),
                'tac_code':fields.char('TAC - First 8 digits from IMEI',size=20),
                'device_type':fields.many2one('device.type.master', 'Device Type'),
    }
    _rec_name = 'tac_code'
    _sql_constraints = [
                ('tac_code_name_uniq', 'unique(tac_code)', 'TAC Code must be unique!'),
    ]

tac_code_master()


####### master to have device types as seperate for classification of Phone,Tablets and Pucks
class device_type_master(osv.osv):
    _name = 'device.type.master'
    _description = "Device Type Master"
    _columns = {
                'name': fields.char('Device Type', size=40),
    }
device_type_master()

class phone_model_master(osv.osv):
    _name = 'phone.model.master'
    _description = "Phone Model Master"
    _columns = {
                'name':fields.char('Phone Model', size=64),
    }
phone_model_master()

class phone_type_master(osv.osv):
    _name = 'phone.type.master'
    _description = "Phone Type Master"
    _columns = {
                'name': fields.char('Phone Type', size=40),
    }
phone_type_master()

class discount_type_master(osv.osv):
    _name = 'discount.type.master'
    _columns = {
                'name':fields.char('Discount Type'),
                'sequence':fields.integer('Sequence'),
                'active':fields.boolean('Active')
        }
    _order = 'sequence'

    _defaults = {
		'active':True
		}
discount_type_master()

class offer_coupon_code(osv.osv):
    _name = 'offer.coupon.code'
    _columns = {
                'coupon_code':fields.char('Coupon Code', required="1"),
                'amount':fields.float('Amount', required="1"),
                'start_date':fields.date('Start Date', required="1"),
                'end_date':fields.date('End Date', required="1"),
                'offset_day':fields.integer('Offset #'),
                'max_end_date':fields.date('Maximum End Date'),
                'active':fields.boolean('Active'),
                'qty_limit':fields.integer('Quantity Limit'),
                'dsr_disc_type':fields.many2many('discount.type.master','offer_disc_type_rel','offer_id','disc_id','Offer Type'),
                'store_id':fields.many2many('sap.store','offer_sto_tbl_rel','offer_id','sto_id','Stores'),
                'market_id':fields.many2many('market.place','offer_mkt_tbl_rel','offer_id','mkt_id','Markets'),
                'region_id':fields.many2many('market.regions','offer_reg_tbl_rel','offer_id','reg_id','Regions'),
                'store_type':fields.many2many('stores.classification','offer_sto_type_rel','offer_id','sto_type_id','Store Type'),
                'include_tac_ids':fields.many2many('tac.code.master','offer_tac_code_rel','offer_id','tac_id','Applicable TAC Codes')
    }

    _defaults = {
                'active':True
    }

    _rec_name = 'coupon_code'

    def create(self, cr, uid, vals, context=None):
        end_date = vals['end_date']
        if vals.has_key('offset_day'):
            offset = vals['offset_day']
        else:
            offset = 0
        max_end_date = (datetime.datetime.strptime(end_date,'%Y-%m-%d') + relativedelta(days=offset))
        max_end_date = max_end_date.strftime('%Y-%m-%d')
        vals.update({'max_end_date':max_end_date})
        res = super(offer_coupon_code,self).create(cr, uid, vals, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int,long)):
            ids = [ids]
        self_data = self.browse(cr, uid, ids)
        if 'end_date' in vals:
            end_date = vals['end_date']
        else:
            end_date = self_data.end_date
        if 'offset_day' in vals:
            offset = vals['offset_day']
        else:
            offset = self_data.offset_day
        max_end_date = (datetime.datetime.strptime(end_date,'%Y-%m-%d') + relativedelta(days=offset))
        max_end_date = max_end_date.strftime('%Y-%m-%d')
        vals.update({'max_end_date':max_end_date})
        res = super(offer_coupon_code,self).write(cr, uid, ids, vals, context=context)
        return res

offer_coupon_code()

############# Credit Class Type Master ##########################
class credit_class_type(osv.osv):
    _name = 'credit.class.type'
    _description = "Credit Class Type"
    _columns = {
                'name':fields.char('Name', size=25),
    }
credit_class_type()

############# Credit Class Master ##############################
class credit_class(osv.osv):
    _name = 'credit.class'
    _description = "Credit Class Category"
    _columns = {
                'name': fields.char('Code', size=64),
                'line_limit': fields.float('Approved Line Limit'),
                'approved_line':fields.many2one('credit.line.limit','Approved Line Limit'),
                'rrp_plan': fields.float('Deposit Regular Rate Plan (RRP)'),
                'rate_lines':fields.one2many('credit.rate.lines','credit_class_id','Rate Plan lines(rate per lines)'),
                'rpo_plan': fields.float('Deposit Rate Plan Only (RPO)'),
                'addon_lines_available': fields.integer('Add-On Lines Available'),
                'addon_deposit_rrp': fields.float('Add-On Deposit Regular Rate Plan (RRP)'),
                'addon_deposit_rpo': fields.float('Add-on Deposit Rate Plan Only (RPO)'),
                'category_type':fields.many2one('credit.class.type','Category Type'),
                'comments': fields.text('Comments'),
                'is_scnc':fields.boolean('Applicable for SCNC SOC codes'),
                'prod_type':fields.many2one('product.category', 'Product Type'),
                'is_emp_upg':fields.boolean('Applicable for Employee Act')
    }
credit_class()

class credit_line_limit(osv.osv):
    _name = 'credit.line.limit'
    _columns = {
                'sequence':fields.integer('Sequence'),
                'name':fields.char('Line'),
    }
    _order = 'sequence'

credit_line_limit()

class transaction_line_soc_rel(osv.osv):
    _name = 'transaction.line.soc.rel'
    _columns = {
                'line_no':fields.many2one('credit.line.limit','Line #'),
                'eligible_spiff':fields.boolean('Spiff'),
                'eligible_commission':fields.boolean('Commission'),
                'eligible_added':fields.boolean('Added Revenue'),
                'eligible_bonus_comm':fields.boolean('Bonus Line Spiff'),
                'eligible_bonus_spiff':fields.boolean('Bonus Handset Spiff'),
                'sub_soc_code':fields.many2one('product.product','Subordinate SOC Code'),
                'soc_code':fields.many2one('product.product','Main SOC Code')
    }

    _defaults = {
                'eligible_spiff':True,
                'eligible_commission':True,
                'eligible_added':True,
                'eligible_bonus_comm':True,
                'eligible_bonus_spiff':True
    }
transaction_line_soc_rel()

"""This class will show Dealer Code"""
class dealer_class(osv.osv):
    _name='dealer.class'
    _description="Dealer Class Category"
    
    # def _get_pre_name(self, cr, uid, context=None):
    #     name = ''
    #     self_ids = self.search(cr, uid, [('dealer_id','=',),('start_date','<=',datetime.datetime.now(pytz.timezone('US/Mountain'))),('end_date','>=',datetime.datetime.now(pytz.timezone('US/Mountain')))])
    #     if self_ids:
    #         self_data = self.browse(cr, uid, self_ids[0])
    #         name = self_data.name
    #     return name

    # def _get_pre_store_name(self, cr, uid, context=None):
    #     name = None
    #     self_ids = self.search(cr, uid, [('start_date','<=',datetime.datetime.now(pytz.timezone('US/Mountain'))),('end_date','>=',datetime.datetime.now(pytz.timezone('US/Mountain')))])
    #     if self_ids:
    #         self_data = self.browse(cr, uid, self_ids[0])
    #         name = self_data.store_name.id
    #     return name

    # def _get_pre_end_date(self, cr, uid, context=None):
    #     name = None
    #     self_ids = self.search(cr, uid, [('start_date','<=',datetime.datetime.now(pytz.timezone('US/Mountain'))),('end_date','>=',datetime.datetime.now(pytz.timezone('US/Mountain')))])
    #     if self_ids:
    #         self_data = self.browse(cr, uid, self_ids[0])
    #         name = self_data.end_date
    #         end_date = datetime.datetime.now(pytz.timezone('US/Mountain')) - relativedelta(days=1)
    #         self.write(cr, uid, self_ids[0],{'end_date':end_date})
    #     return name

    # def _get_pre_emp_type(self, cr, uid, context=None):
    #     name = None
    #     self_ids = self.search(cr, uid, [('start_date','<=',datetime.datetime.now(pytz.timezone('US/Mountain'))),('end_date','>=',datetime.datetime.now(pytz.timezone('US/Mountain')))])
    #     if self_ids:
    #         self_data = self.browse(cr, uid, self_ids[0])
    #         name = self_data.emp_type.id
    #     return name

    _columns= {
                'name':fields.char('Dealer Code',size=64,required="1"),
                'store_name': fields.many2one('sap.store', 'Sap Number',required="1"),
                'dealer_id':fields.many2one('hr.employee','Employee',required="1"),
                'start_date': fields.date('Start Date',required="1"),
                'end_date': fields.date('End Date',required="1"),
                'designation_id':fields.many2one('hr.job','Designation'),
                'emp_type':fields.many2one('hr.employee.type','Employee Type',required="1"),
                'move_type':fields.selection([('temp','Temporary'),('perm','Permanent')],'Movement Type',required="1"),
    }
    _order = 'start_date asc, end_date asc'
    # _defaults = {
    #             'name':_get_pre_name,
    #             'store_name':_get_pre_store_name,
    #             'start_date':datetime.datetime.now(pytz.timezone('US/Mountain')),
    #             'end_date':_get_pre_end_date,
    #             'emp_type':_get_pre_emp_type
    # }

    def open_entry_update_wizard(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        self_data = self.browse(cr, uid, ids[0])
        start_date = self_data.start_date
        todays_date = datetime.datetime.now(pytz.timezone('US/Mountain')).strftime('%Y-%m-%d')
        if self_data.end_date < todays_date:
            end_date = self_data.end_date
        else:
            end_date = todays_date
        emp_id = self_data.dealer_id.id
        dealer_code_upg = self_data.name
        sap_id_upg = self_data.store_name.id
        context = dict(context, start_date=start_date, end_date=end_date, emp_id=emp_id, dealer_code_upg=dealer_code_upg, sap_id_upg=sap_id_upg)
        return {
            # 'name': _('Commission Tracker'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wireless.dsr.manually.update',
            # 'views': [(compose_form.id, 'form')],
            'view_id': False,
            'target': 'new',
            # 'res_id': ids[0],
            'context': context,
        }

    def create(self, cr, uid, vals, context=None):
        hr_table =self.pool.get('hr.employee')
        res_users_table = self.pool.get('res.users')
        sap_obj = self.pool.get('sap.store')

        dealer_id = vals['dealer_id']
        end_date = vals['end_date']
        start_date = vals['start_date']
        store_name = vals['store_name']
        emp_type = vals['emp_type']

        res_id = super(dealer_class, self).create(cr, uid, vals, context=context)
        if not dealer_id:
            dealer_id = self.browse(cr, uid, res_id).dealer_id.id

        if start_date > end_date:
            raise osv.except_osv(('Warning!!!'),('End date should be greater than start date'))        
        
        dealer_data_ids = self.search(cr, uid, [('dealer_id','=',dealer_id),('start_date','<=',start_date),('end_date','>=',end_date)])
        if len(dealer_data_ids) > 1:
            raise osv.except_osv(('Warning!!'),('Please change end date in previous dealer code.'))

        dealer_data_ids = self.search(cr, uid, [('dealer_id','=',dealer_id),('end_date','>=',start_date)])
        if len(dealer_data_ids) > 1:
            raise osv.except_osv(('Warning!!'),('Please change end date in previous dealer code.'))
        
############ context param passed from user's create function to skip updating of SAP in user's master if user is being created ###
        if 'user_create' in context:
            user_create = context['user_create']
        else:
            user_create = False

        # today_date = datetime.datetime.now(pytz.timezone('US/Mountain')).strftime('%Y-%m-%d'
        search_ids = self.search(cr, uid, [('dealer_id','=',dealer_id)], order='end_date desc', limit=1)
        if search_ids:
            self_data = self.browse(cr, uid, search_ids[0])
            hr_table.write(cr, uid, [self_data.dealer_id.id], {'employment_type':self_data.emp_type.id,'store_id':self_data.store_name.id})

####### checking based on parameter passed from user'create #########
            if not user_create:
                user_id = self_data.dealer_id.user_id.id
                sap_data = sap_obj.browse(cr, uid, self_data.store_name.id)
                market_id = sap_data.market_id.id
                region_id = sap_data.market_id.region_market_id.id
                res_users_table.write(cr, uid, user_id, {'sap_id':self_data.store_name.id,'market_id':market_id,'region_id':region_id})

        return res_id

    def write(self, cr, uid, ids, vals, context=None):
        hr_obj = self.pool.get('hr.employee')
        sap_obj = self.pool.get('sap.store')

        self_data = self.browse(cr, uid, ids[0])
        if 'end_date' in vals:
            end_date = vals['end_date']
        else:
            end_date = self_data.end_date
        if 'start_date' in vals:
            start_date = vals['start_date']
        else:
            start_date = self_data.start_date
        if 'emp_type' in vals:
            emp_type = vals['emp_type']
        else:
            emp_type = self_data.emp_type.id
        if 'store_name' in vals:
            store_name = vals['store_name']
        else:
            store_name = self_data.store_name.id        
        dealer_id = self_data.dealer_id.id
        
        if start_date > end_date:
            raise osv.except_osv(('Warning!!!'),('End date should be greater than start date'))

        res = super(dealer_class, self).write(cr, uid, ids, vals, context=context)
        
        dealer_data_ids = self.search(cr, uid, [('dealer_id','=',dealer_id),('start_date','<=',start_date),('end_date','>=',end_date)])
        if len(dealer_data_ids) > 1:
            raise osv.except_osv(('Warning!!'),('Period for which you are updating dealer code already exist.'))

        dealer_data_ids = self.search(cr, uid, [('dealer_id','=',dealer_id),('end_date','>=',start_date), ('start_date','<',end_date)])
        if len(dealer_data_ids) > 1:
            raise osv.except_osv(('Warning!!'),('Previous dealer code exist on this start date.'))

        # today_date = datetime.datetime.now(pytz.timezone('US/Mountain')).strftime('%Y-%m-%d')
        # if (start_date <= today_date) and (end_date >= today_date):
        search_ids = self.search(cr, uid, [('dealer_id','=',dealer_id)], order='end_date desc', limit=1)
        if search_ids:
            self_data = self.browse(cr, uid, search_ids[0])
            hr_obj.write(cr, uid, [self_data.dealer_id.id], {'employment_type':self_data.emp_type.id,'store_id':self_data.store_name.id})

            user = self_data.dealer_id.user_id.id
            sap_data = sap_obj.browse(cr, uid, self_data.store_name.id)
            market_id = sap_data.market_id.id
            region_id = sap_data.market_id.region_market_id.id
            self.pool.get('res.users').write(cr, uid, [user], {'sap_id':self_data.store_name.id,'market_id':market_id,'region_id':region_id})

        return res

    def unlink(self, cr, uid, ids, context=None):
        res = {}
        hr_obj = self.pool.get('hr.employee')
        user_obj = self.pool.get('res.users')
        self_record_data = self.browse(cr, uid, ids[0])
        try:
            del_hr_id = self_record_data.dealer_id.id
        except:
            return True
        user_id = self_record_data.dealer_id.user_id.id
        today_date = datetime.datetime.now(pytz.timezone('US/Mountain')).strftime('%Y-%m-%d')
        res = super(dealer_class, self).unlink(cr, uid, ids, context=context)
        cr.commit()
        dealer_date_search = self.search(cr, uid, [('dealer_id','=',del_hr_id)], order='end_date desc', limit=1)
        if dealer_date_search:
            dealer_current_data = self.browse(cr, uid, dealer_date_search[0])
            store_id = dealer_current_data.store_name.id
            market_id = dealer_current_data.store_name.market_id.id
            region_id = dealer_current_data.store_name.market_id.region_market_id.id
            emp_type = dealer_current_data.emp_type and dealer_current_data.emp_type.id or False
            hr_obj.write(cr, uid, [del_hr_id], {'store_id':store_id,'employment_type':emp_type})
            user_obj.write(cr, uid, [user_id], {'sap_id':store_id,'market_id':market_id,'region_id':region_id})
        else:
            raise osv.except_osv(('Alert!!'),('There must be at least one record in Dealer Code master.'))
        return res

dealer_class()

class product_template(osv.osv):
    _inherit = 'product.template'

product_template()

class product_price_history(osv.osv):
    _inherit = 'product.price.history'

product_price_history()

################# Discount Master ####################
class discount_master(osv.osv):
    _name = 'discount.master'
    _description = "Discount Master"
    _columns = {
                'name':fields.char('Code', size=5),
                'disc_percent':fields.integer('Discount Percent(%)'),
    }
    _rec_name = "disc_percent"

discount_master()

################### Porting Companies Name Master ######################
class port_company(osv.osv):
    _name= "port.company"
    _description = "List of companies for porting number"
    _columns = {
                'name':fields.char('Company', size=64),
                'sequence':fields.integer('Sequence'),
                'active':fields.boolean('Active')
    }
    _order = 'sequence'

    _defaults = {
                'active':True
    }
    
port_company()

################## Credit Rate Lines Master #############################
class credit_rate_lines(osv.osv):
    _name = "credit.rate.lines"
    _description = "Credit Class Rate Lines"
    _columns = {
                'name':fields.char('Line Name', size=15),
                'deposit_amt':fields.float('Deposit'),
                'credit_class_id':fields.many2one('credit.class','Credit Class'),
    }
credit_rate_lines()

############### Revenue Formula Master ####################################
class revenue_generate_master(osv.osv):
    _name = 'revenue.generate.master'
    _description = "Revenue Configuration Master"
    _columns = {
                'name':fields.char('Revenue formula name', size=64, required=True),
                'inactive':fields.boolean('Inactive'),
                'dsr_prod_type':fields.many2one('product.category', 'Product Type', required=True),
                'dsr_prod_code_type':fields.many2one('product.category', 'Product Code Type'),
                'dsr_rev_product':fields.many2one('product.product', 'Product'),
                'dsr_credit_class_type':fields.many2one('credit.class.type', 'Credit Class Type'),
                'dsr_activation_type':fields.selection([('at_act','At Time of Activation'),('after_act','After Activation')], 'Activation Interval'),
                'dsr_revenue_calc':fields.float('Revenue Calculation Formula (* MRC)', required=True),
                'dsr_phone_spiff':fields.float('Phone Spiff Formula (* MRC)', required=True),
                'dsr_added_rev':fields.float('Added Revenue', required=True),
                'dsr_start_date':fields.date('Start Date', required=True),
                'dsr_end_date':fields.date('End Date', required=True),
                'dsr_jod':fields.boolean('JUMP on Demand'),
                'is_exclude':fields.boolean('Exclude ?'),
                'notes':fields.text('Notes'),
                'exclude_scnc':fields.boolean('Exclude SCNC'),
                'exclude_tac_code':fields.many2many('tac.code.master','rev_formula_master_tac_rel','rev_formula_id','tac_id','TAC Code'),
                'bonus_line_spiff':fields.float('Bonus Line Spiff'),
                'bonus_handset_spiff':fields.float('Bonus Handset Spiff'),

    }
    _defaults = {
                'dsr_jod':False
    }
    _sql_constraints = [
                ('revenue_formula_name_uniq', 'unique(name)', 'Revenue formula name must be unique!'),
    ]
revenue_generate_master()

class lock_down_master(osv.osv):
    _name = 'lock.down.master'
    _description = "Lock Down Date Master"
    _columns = {
                'date':fields.integer('Lock Down Date'),
                'inactive':fields.boolean('Inactive'),
                'group_lock_rel':fields.many2many('res.groups','group_lock_rel_master','gid','lid','Related Group'),
                'unlock_start_date':fields.date('Ship-to Unlock Start Date'),
                'unlock_end_date':fields.date('Ship-to Unlock End Date')
    }
lock_down_master()

class dsr_hear_about_us(osv.osv):
    _name = 'dsr.hear.about.us'
    _columns = {
                'name':fields.char('Name'),
                'sequence':fields.integer('Sequence'),
    }
    _order = 'sequence'
dsr_hear_about_us()

class dsr_employee_type(osv.osv):
    _name = 'dsr.employee.type'
    _columns = {
                'name':fields.char('Name'),
                'is_emp_upg':fields.boolean('Employee Upgrade')
    }
dsr_employee_type()

################ Wireless DSR Process Master ########################
class wireless_dsr(osv.osv):
    _name = 'wireless.dsr'
    _description = "Wireless DSR Process"
    _order = 'id desc'

    def _get_prepaid_lines(self, cr, uid, ids, fields, args, context=None):
        line_obj = self.pool.get('wireless.dsr.prepaid.line')
        res = {}
        for script in self.browse(cr, uid, ids):
            line_ids = line_obj.search(cr, uid, [('product_id','=',script.id),('created_feature','=',False)])
            res[script.id] = line_ids
        return res

    def _set_prepaid_lines(self, cr, uid, id, name, value, inv_arg, context):
        line_obj = self.pool.get('wireless.dsr.prepaid.line')
        for line in value:
            if line[0] == 1: # one2many Update
                line_id = line[1]
                line_obj.write(cr, uid, [line_id], line[2])
            elif line[0] == 0: # one2many create
                line[2]['product_id'] = id
                line_obj.create(cr, uid, line[2])
            elif line[0] == 2: # one2many delete
                line_obj.unlink(cr, uid, [line[1]])
        return True

    def _get_feature_lines(self, cr, uid, ids, fields, args, context=None):
        line_obj = self.pool.get('wireless.dsr.feature.line')
        res = {}
        for script in self.browse(cr, uid, ids):
            line_ids = line_obj.search(cr, uid, [('feature_product_id','=',script.id),('created_upgrade','=',False),('dsr_activiation_interval','=','after_act')])
            res[script.id] = line_ids
        return res

    def _set_feature_lines(self, cr, uid, id, name, value, inv_arg, context):
        line_obj = self.pool.get('wireless.dsr.feature.line')
        for line in value:
            if line[0] == 1: # one2many Update
                line_id = line[1]
                line_obj.write(cr, uid, [line_id], line[2])
            elif line[0] == 0: # one2many create
                line[2]['feature_product_id'] = id
                line_obj.create(cr, uid, line[2])
            elif line[0] == 2: # one2many delete
                line_obj.unlink(cr, uid, [line[1]])
        return True

    def _compute_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        pre_obj = self.pool.get('wireless.dsr.prepaid.line')
        feature_obj = self.pool.get('wireless.dsr.feature.line')
        order = self.browse(cr, uid, ids[0])
        trans_date = order.dsr_date
        emp_des = order.dsr_designation_id.id
        comm_percent = 0.00
        #base_comm_obj = self.pool.get('comm.basic.commission.formula')
        #base_comm_search = base_comm_obj.search(cr, uid, [('comm_designation','=',emp_des),('comm_start_date','<=',trans_date),('comm_end_date','>=',trans_date),('comm_inactive','=',False)])
        #if base_comm_search:
        #   comm_percent = base_comm_obj.browse(cr, uid, base_comm_search[0]).comm_percent
        #else:
        #    base_comm_search = base_comm_obj.search(cr, uid, [('comm_start_date','<=',trans_date),('comm_end_date','>=',trans_date),('comm_inactive','=',False)])
        #    if base_comm_search:
        #        comm_percent = base_comm_obj.browse(cr, uid, base_comm_search[0]).comm_percent
        res[order.id] = {
            'gross_rev': 0.0,
            'gross_comm_per_line': 0.0
        }
        val = val1 = 0.0
        cr.execute("select id from wireless_dsr_prepaid_line where product_id = %s"%(order.id))
        pre_ids = map(lambda x: x[0], cr.fetchall())
        cr.execute("select id from wireless_dsr_feature_line where feature_product_id = %s"%(order.id))
        feature_ids = map(lambda x: x[0], cr.fetchall())
        for line in order.postpaid_product_line:
            val += line.dsr_rev_gen
            val1 += line.dsr_comm_per_line
        for line in pre_obj.browse(cr, uid, pre_ids):
            val += line.dsr_rev_gen
            val1 += line.dsr_comm_per_line
        for line in order.upgrade_product_line:
            val += line.dsr_rev_gen
            val1 += line.dsr_comm_per_line
        for line in feature_obj.browse(cr, uid, feature_ids):
            val += line.dsr_rev_gen
            val1 += line.dsr_comm_per_line
        for line in order.acc_product_line:
            # disc = 0.00
            # add = line.dsr_list_price * line.dsr_quantity
            # if line.dsr_disc_percent:
            #     disc = (add * line.dsr_disc_percent.disc_percent)/100
            # if line.dsr_acc_comm <= 0.00 and (not line.dsr_sku_select.non_comm):
            #     rev = 0.35 * (add - disc)
            # elif line.dsr_sku_select.non_comm:
            #     rev = 0.00
            # else:
            #     rev = (line.dsr_acc_comm * line.dsr_quantity) - disc
            val += line.dsr_rev_gen
            val1 += line.dsr_comm_per_line
            
        res[order.id]['gross_rev'] = val
        res[order.id]['gross_comm_per_line'] = val1
        return res

    # def _get_order(self, cr, uid, ids, context=None):
    #     result = {}
    #     for line in self.pool.get('wireless.dsr.postpaid.line').browse(cr, uid, ids, context=context):
    #         result[line.product_id.id] = True
    #     for line in self.pool.get('wireless.dsr.upgrade.line').browse(cr, uid, ids, context=context):
    #         result[line.product_id.id] = True
    #     for line in self.pool.get('wireless.dsr.prepaid.line').browse(cr, uid, ids, context=context):
    #         result[line.product_id.id] = True
    #     for line in self.pool.get('wireless.dsr.feature.line').browse(cr, uid, ids, context=context):
    #         result[line.feature_product_id.id] = True
    #     for line in self.pool.get('wireless.dsr.acc.line').browse(cr, uid, ids, context=context):
    #         result[line.product_id.id] = True
    #     return result.keys()


    def _compute_disc(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        order = self.browse(cr, uid, ids[0])
        res[order.id] = {
            'gross_disc': 0.0
        }
        val = val1 = 0.0
        for line in order.dsr_offer_ids:
            val += line.dsr_discount
        res[order.id]['gross_disc'] = val
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('wireless.dsr').browse(cr, uid, ids, context=context):
            result[line.id] = True
        return result.keys()

    def _get_date_mst(self,cr, uid, fields, context=None):
	### returns mountain time
        return datetime.datetime.now(pytz.timezone('US/Mountain')).date()


    _columns = {
                'name':fields.char('Entry No.', size=64, readonly=True),
                'dsr_dealer_code':fields.char('Dealer Code', size=64),
                'dsr_designation_id':fields.many2one('hr.job', 'Designation'),
                'dsr_date':fields.date('Transaction Date'),
                'pseudo_date':fields.date('Pseudo Transaction Date'),
                'dsr_date_order':fields.date('Submission Date'),
                'dsr_cust_name':fields.char('Customer Name', size=256, help="Enter Customer Name."),
                'dsr_transaction_id':fields.char('Transaction ID', size=64),
                'dsr_how_he_hear':fields.many2one('dsr.hear.about.us', 'How did you hear about us?'),
                # 'dsr_acct_mobile_no':fields.char('Account Mobile #', size=10),
                'dsr_cust_email_id':fields.char('Email Address', size=64),
                'dsr_sales_employee_id':fields.many2one('hr.employee', 'Sales Representative'),
                'dsr_offer_ids':fields.one2many('dsr.marketing.offers','dsr_id','Marketing Offer Lines'),
                'is_offer':fields.boolean('Marketing Offer'),
                'dsr_store_id':fields.many2one('sap.store', 'Home/Base store'),
                'dsr_store_type':fields.many2one('stores.classification','Type of Store'),
                'dsr_market_id':fields.many2one('market.place', 'Market'),
                'dsr_region_id':fields.many2one('market.regions', 'Region'),
                'is_postpaid':fields.boolean('Postpaid'),
                'is_prepaid':fields.boolean('Prepaid'),
                'is_upgrade':fields.boolean('Upgrade'),
                'is_feature':fields.boolean('Feature'),
                'is_accessory':fields.boolean('Accessory'),
                'dsr_prod_type1':fields.selection(_prod_type, 'Transaction Type'),
                'dsr_prod_type2':fields.selection(_prod_type, 'Transaction Type'),
                'dsr_prod_type3':fields.selection(_prod_type, 'Transaction Type'),
                'dsr_prod_type4':fields.selection(_prod_type, 'Transaction Type'),
                'dsr_prod_type5':fields.selection(_prod_type, 'Transaction Type'),
                'acc_product_line':fields.one2many('wireless.dsr.acc.line','product_id','Accessory Lines'),
                # 'upgrade_acc_product_line':fields.one2many('wireless.dsr.upgrade.acc.line','product_id','Accessory Lines'),
                # 'postpaid_acc_product_line':fields.one2many('wireless.dsr.postpaid.acc.line','product_id','Accessory Lines'),
                'postpaid_product_line':fields.one2many('wireless.dsr.postpaid.line','product_id','Postpaid Lines'),
                'prepaid_product_line':fields.function(_get_prepaid_lines, fnct_inv=_set_prepaid_lines, string='Prepaid Lines', relation="wireless.dsr.prepaid.line", method=True, type="one2many"),
                # 'postpaid_feature_product_line':fields.one2many('wireless.dsr.postpaid.feature.line','feature_product_id','Feature Lines'),
                'feature_product_line':fields.function(_get_feature_lines, fnct_inv=_set_feature_lines, relation='wireless.dsr.feature.line',string='Feature Lines',method=True, type="one2many"),
                # 'upgrade_feature_product_line':fields.one2many('wireless.dsr.upgrade.feature.line','feature_product_id','Feature Lines'),
                'upgrade_product_line':fields.one2many('wireless.dsr.upgrade.line','product_id','Upgrade Lines'),
                'state':fields.selection([('draft','Draft'),('pending','Pending'),('cancel','Cancel'),('submit','Submit'),('void','VOID'),('done','Done')],'Status', readonly=True),
                'notes':fields.text('System Notes'),
                'dsr_notes':fields.text('DSR Notes'),
                'history_dsr_id':fields.char('Historical DSR ID'),
                'market_name':fields.char('Market Name'),
                'store_name':fields.char('Store Name'),
                'gross_rev':fields.function(_compute_all, string="Gross Rev.", type="float", multi="sums",store=True),
                'gross_disc':fields.function(_compute_disc, string="Gross Discount", type="float",multi="sums",
                    store={
                                'wireless.dsr': (_get_order, ['dsr_offer_ids'], 10),
                    }),
                'gross_comm_per_line':fields.function(_compute_all, string="Gross Commission", type="float", multi="sums", store=True)
    }
    _defaults = {
                'name': lambda obj, cr, uid, context: 'WV',
                'state':'draft',
                #'dsr_date': lambda *a: time.strftime('%Y-%m-%d'),
#                'dsr_date':datetime.datetime.now(pytz.timezone('US/Mountain')).date(),
                'dsr_date': _get_date_mst,
                # 'prepaid_product_line': lambda self, cr, uid, context: context.get('created_feature', False)
    }

    # def _auto_init(self, cr, context=None):
    #     res = super(wireless_dsr, self)._auto_init(cr, context=context)
    #     cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = \'wireless_dsr_dsr_date_index\'')
    #     if not cr.fetchone():
    #         cr.execute('CREATE INDEX wireless_dsr_dsr_date_index ON wireless_dsr (dsr_date)')
    #     # cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = %s', ('account_move_line_date_id_index',))
    #     # if not cr.fetchone():
    #     #     cr.execute('CREATE INDEX account_move_line_date_id_index ON account_move_line (date DESC, id desc)')
    #     return res

    def onchange_is_pos(self, cr, uid, ids, postpaid):
        if postpaid == False:
            return {'value': {'postpaid_product_line':False}}
        return{}

    def onchange_is_pre(self, cr, uid, ids, prepaid):
        if prepaid == False:
            return {'value': {'prepaid_product_line':False}}
        return{}

    def onchange_is_upg(self, cr, uid, ids, upgrade):
        if upgrade == False:
            return {'value': {'upgrade_product_line':False}}
        return{}

    def onchange_is_fea(self, cr, uid, ids, feature):
        if feature == False:
            return {'value': {'feature_product_line':False}}
        return{}

    def onchange_is_acc(self, cr, uid, ids, accessory):
        if accessory == False:
            return {'value': {'acc_product_line':False}}
        return{}

    def _write_act_date_new(self, cr, uid, ids):
        dsr_data = self.browse(cr, uid, ids[0])
        trans_date = dsr_data.dsr_date
        postpaid_line_data = dsr_data.postpaid_product_line
        if postpaid_line_data:
            for postpaid_line_id in postpaid_line_data:
                pos_id = postpaid_line_id.id
                self.pool.get('wireless.dsr.postpaid.line').write(cr, uid, [pos_id], {'dsr_act_date_new':trans_date})
        return True

    def check_same_phone(self, cr, uid, ids):
        dsr_data = self.browse(cr, uid, ids[0])
        pos_line_data = dsr_data.postpaid_product_line
        pre_line_data = dsr_data.prepaid_product_line
        if pre_line_data and pos_line_data:
            for pos_line_id in pos_line_data:
                pos_id = pos_line_id.id
                pos_data = self.pool.get('wireless.dsr.postpaid.line').browse(cr, uid, pos_id)
                pos_phone_num = pos_data.dsr_phone_no
                pre_search = self.pool.get('wireless.dsr.prepaid.line').search(cr, uid, [('product_id','=',ids[0]),('dsr_phone_no','=',pos_phone_num)])
                if pre_search:
                    raise osv.except_osv(_('Warning'),_("Same mobile number found in Postpaid and Prepaid records."))
        return True

    def check_imei_records(self, cr, uid, ids):
        dsr_data = self.browse(cr, uid, ids[0])
        pos_line_data = dsr_data.postpaid_product_line
        upgrade_line_data = dsr_data.upgrade_product_line
        if pos_line_data:
            for pos_line_id in pos_line_data:
                pos_id = pos_line_id.id
                pos_data = self.pool.get('wireless.dsr.postpaid.line').browse(cr, uid, pos_id)
                pos_imei = pos_data.dsr_imei_no
                pos_eip = pos_data.dsr_eip_no
                pos_phone_purchase = pos_data.dsr_phone_purchase_type
                if (not pos_imei) and (pos_phone_purchase != 'sim_only'):
                    raise osv.except_osv(_('Warning'),_("IMEI # not found in Postpaid Line which is required for record to be in done state."))
                if (not pos_eip) and (pos_phone_purchase == 'new_device'):
                    raise osv.except_osv(('Warning!'),("EIP # not found in Postpaid Line which is required for record to be in done state."))
        if upgrade_line_data:
            for upg_line_id in upgrade_line_data:
                upg_id = upg_line_id.id
                upg_data = self.pool.get('wireless.dsr.upgrade.line').browse(cr, uid, upg_id)
                upg_imei = upg_data.dsr_imei_no
                if not upg_imei:
                    raise osv.except_osv(_('Warning'),_("IMEI # not found in Upgrade Line which is required for record to be in done state.."))
        return True

    def unlink(self, cr, uid, ids, context=None):
        dsr_data = self.browse(cr, uid, ids)
        pos_obj = self.pool.get('wireless.dsr.postpaid.line')
        pre_obj = self.pool.get('wireless.dsr.prepaid.line')
        upg_obj = self.pool.get('wireless.dsr.upgrade.line')
        fet_obj = self.pool.get('wireless.dsr.feature.line')
        acc_obj = self.pool.get('wireless.dsr.acc.line')
        for dsr_data_id in dsr_data:
            state = dsr_data_id.state
            #if state == 'draft': commented by shashank on 25/11
            #import ipdb;ipdb.set_trace()
            if state:
                dsr_id = dsr_data_id.id
                pos_search = pos_obj.search(cr, uid, [('product_id','=',dsr_id)])
                if pos_search:
                    pos_obj.unlink(cr, uid, pos_search)
                pre_search = pre_obj.search(cr, uid, [('product_id','=',dsr_id)])
                if pre_search:
                    pre_obj.unlink(cr, uid, pre_search)
                upg_search = upg_obj.search(cr, uid, [('product_id','=',dsr_id)])
                if upg_search:
                    upg_obj.unlink(cr, uid, upg_search)
                fet_search = fet_obj.search(cr, uid, [('feature_product_id','=',dsr_id)])
                if fet_search:
                    fet_obj.unlink(cr, uid, fet_search)
                acc_search = acc_obj.search(cr, uid, [('product_id','=',dsr_id)])
                if acc_search:
                    acc_obj.unlink(cr, uid, acc_search)
            else:
                raise osv.except_osv(_('Warning'),_("You can delete Sales Entry only in Draft State."))
        res = super(wireless_dsr, self).unlink(cr, uid, ids, context=context)
        return res

    def check_imei_records_pending(self, cr, uid, ids):
        dsr_data = self.browse(cr, uid, ids[0])
        pos_line_data = dsr_data.postpaid_product_line
        if pos_line_data:
            for pos_line_id in pos_line_data:
                pos_id = pos_line_id.id
                pos_data = self.pool.get('wireless.dsr.postpaid.line').browse(cr, uid, pos_id)
                pos_imei = pos_data.dsr_imei_no
                pos_phone_purchase = pos_data.dsr_phone_purchase_type
                ship_to = pos_data.dsr_ship_to
                if (not pos_imei) and (pos_phone_purchase != 'sim_only') and (not ship_to):
                    raise osv.except_osv(_('Warning'),_("IMEI # not found in Postpaid Line which is required for record to be in done state."))
        return True

# ****************** Move parent and child records to Pending state ******************* #
    def dsr_pending(self, cr, uid, ids, context=None):
        dsr_data = self.browse(cr, uid, ids[0])
        self.check_imei_records_pending(cr, uid, ids)
        pre_obj = self.pool.get('wireless.dsr.prepaid.line')
        fea_obj = self.pool.get('wireless.dsr.feature.line')
        pos_line_data = dsr_data.postpaid_product_line
        upgrade_line_data = dsr_data.upgrade_product_line
        acc_line_data = dsr_data.acc_product_line
        pre_line_data = pre_obj.search(cr, uid, [('product_id','=',ids[0])])
        fea_line_data = fea_obj.search(cr, uid, [('feature_product_id','=',ids[0])])
       # import ipdb;ipdb.set_trace()
        if pos_line_data:
            for pos_line_id in pos_line_data:
                pos_id = pos_line_id.id
                self.pool.get('wireless.dsr.postpaid.line').write(cr, uid, [pos_id], {'state':'pending'})
        if upgrade_line_data:
            for upg_line_id in upgrade_line_data:
                upg_id = upg_line_id.id
                self.pool.get('wireless.dsr.upgrade.line').write(cr, uid, [upg_id], {'state':'pending'})
        if acc_line_data:
            for acc_line_id in acc_line_data:
                dsr_sku_select = acc_line_id.dsr_sku_select.id
                if not dsr_sku_select:
                    raise osv.except_osv(('Warning!!'),('Accessory SKU is required.'))
                acc_id = acc_line_id.id
                self.pool.get('wireless.dsr.acc.line').write(cr, uid, [acc_id], {'state':'pending'})
        if pre_line_data:
            for pre_line_id in pre_line_data:
                pre_obj.write(cr, uid, [pre_line_id], {'state':'pending'})
        if fea_line_data:
            for fea_line_id in fea_line_data:
                fea_obj.write(cr, uid, [fea_line_id], {'state':'pending'})
        self.write(cr, uid, ids[0], {'state':'pending'})
        return True

# ****************** Move parent and Child records to Done state *********************** #
    def dsr_submit(self, cr, uid, ids, context=None):        
# ************ Checks same Phone # in Postpaid and Prepaid records ******************** #
        self.check_same_phone(cr, uid, ids)
# **************** Checks IMEI in Postpaid and Upgrade, if they are empty then raises exception ******** #
        self.check_imei_records(cr, uid, ids)
        self._write_act_date_new(cr, uid, ids)
# ************* Postpaid, Upgrade, Accessory records can be fetched through Browse function directly ********** ##        
        dsr_data = self.browse(cr, uid, ids[0])
        pre_obj = self.pool.get('wireless.dsr.prepaid.line')
        fea_obj = self.pool.get('wireless.dsr.feature.line')
        pos_line_data = dsr_data.postpaid_product_line
        upgrade_line_data = dsr_data.upgrade_product_line
        acc_line_data = dsr_data.acc_product_line
        pre_line_data = pre_obj.search(cr, uid, [('product_id','=',ids[0])])
        fea_line_data = fea_obj.search(cr, uid, [('feature_product_id','=',ids[0])])
        #import ipdb;ipdb.set_trace()
        if pos_line_data:
            for pos_line_id in pos_line_data:
                pos_id = pos_line_id.id
                self.pool.get('wireless.dsr.postpaid.line').write(cr, uid, [pos_id], {'state':'done'})
        if upgrade_line_data:
            for upg_line_id in upgrade_line_data:
                upg_id = upg_line_id.id
                self.pool.get('wireless.dsr.upgrade.line').write(cr, uid, [upg_id], {'state':'done'})
        if acc_line_data:
            for acc_line_id in acc_line_data:
                dsr_sku_select = acc_line_id.dsr_sku_select.id
                if not dsr_sku_select:
                    raise osv.except_osv(('Warning!!'),('Accessory SKU is required.'))
                acc_id = acc_line_id.id
                self.pool.get('wireless.dsr.acc.line').write(cr, uid, [acc_id], {'state':'done'})
        if pre_line_data:
            for pre_line_id in pre_line_data:
                pre_obj.write(cr, uid, [pre_line_id], {'state':'done'})
        if fea_line_data:
            for fea_line_id in fea_line_data:
                fea_obj.write(cr, uid, [fea_line_id], {'state':'done'})
        #self.write(cr, uid, ids[0], {'state':'done','dsr_date_order':time.strftime("%Y-%m-%d")})
        # self.write(cr, uid, ids[0], {'state':'done','pseudo_date':pseudo_date,'dsr_date_order':datetime.datetime.now(pytz.timezone('US/Mountain')).date()})
        self.write(cr, uid, ids[0], {'state':'done','dsr_date_order':datetime.datetime.now(pytz.timezone('US/Mountain')).date()})
        return True

# ****************** Move parent and Child records to Cancel state *********************** #
    def dsr_cancel(self, cr, uid, ids, context=None):
        dsr_data = self.browse(cr, uid, ids[0])
        pre_obj = self.pool.get('wireless.dsr.prepaid.line')
        fea_obj = self.pool.get('wireless.dsr.feature.line')
        pos_line_data = dsr_data.postpaid_product_line
        upgrade_line_data = dsr_data.upgrade_product_line
        acc_line_data = dsr_data.acc_product_line
        pre_line_data = pre_obj.search(cr, uid, [('product_id','=',ids[0])])
        fea_line_data = fea_obj.search(cr, uid, [('feature_product_id','=',ids[0])])
        #import ipdb;ipdb.set_trace()
        if pos_line_data:
            for pos_line_id in pos_line_data:
                pos_id = pos_line_id.id
                self.pool.get('wireless.dsr.postpaid.line').write(cr, uid, [pos_id], {'state':'draft'})
        if upgrade_line_data:
            for upg_line_id in upgrade_line_data:
                upg_id = upg_line_id.id
                self.pool.get('wireless.dsr.upgrade.line').write(cr, uid, [upg_id], {'state':'draft'})
        if acc_line_data:
            for acc_line_id in acc_line_data:
                acc_id = acc_line_id.id
                self.pool.get('wireless.dsr.acc.line').write(cr, uid, [acc_id], {'state':'draft'})
        if pre_line_data:
            for pre_line_id in pre_line_data:
                pre_obj.write(cr, uid, [pre_line_id], {'state':'draft'})
        if fea_line_data:
            for fea_line_id in fea_line_data:
                fea_obj.write(cr, uid, [fea_line_id], {'state':'draft'})
        self.write(cr, uid, ids[0], {'state':'draft'})
        return True

# ****************** Move parent and Child records to "Set To Draft" state *********************** #
    def dsr_draft(self, cr, uid, ids, context=None):
        dsr_data = self.browse(cr, uid, ids[0])
        pre_obj = self.pool.get('wireless.dsr.prepaid.line')
        fea_obj = self.pool.get('wireless.dsr.feature.line')
        pos_line_data = dsr_data.postpaid_product_line
        upgrade_line_data = dsr_data.upgrade_product_line
        acc_line_data = dsr_data.acc_product_line
        pre_line_data = pre_obj.search(cr, uid, [('product_id','=',ids[0])])
        fea_line_data = fea_obj.search(cr, uid, [('feature_product_id','=',ids[0])])        
        if pos_line_data:
            for pos_line_id in pos_line_data:
                pos_id = pos_line_id.id
                self.pool.get('wireless.dsr.postpaid.line').write(cr, uid, [pos_id], {'state':'draft'})
        if upgrade_line_data:
            for upg_line_id in upgrade_line_data:
                upg_id = upg_line_id.id
                self.pool.get('wireless.dsr.upgrade.line').write(cr, uid, [upg_id], {'state':'draft'})
        if acc_line_data:
            for acc_line_id in acc_line_data:
                acc_id = acc_line_id.id
                self.pool.get('wireless.dsr.acc.line').write(cr, uid, [acc_id], {'state':'draft'})
        if pre_line_data:
            for pre_line_id in pre_line_data:
                pre_obj.write(cr, uid, [pre_line_id], {'state':'draft'})
        if fea_line_data:
            for fea_line_id in fea_line_data:
                fea_obj.write(cr, uid, [fea_line_id], {'state':'draft'})
        self.write(cr, uid, ids[0], {'state':'draft'})
        return True

    # def dsr_done(self, cr, uid, ids, context=None):
    #     self.write(cr, uid, ids[0], {'state':'done'})
    #     return True

# ****************** Move parent and Child records to "Void" state *********************** #
    def dsr_void(self, cr, uid, ids, context=None):
        ctx = (context or {}).copy()
        ctx['active_id'] = ids[0]
        return {
            'name': _('Move to VOID'),
            'view_type':'form',
            'view_mode':'form',
            'res_model':'wireless.dsr.void.wizard',
            'view_id':False,
            'type':'ir.actions.act_window',
            'context':ctx,
            'target':'new'
        }

    def onchange_email(self, cr, uid, ids, email):
        if email:
            email_match(email)
            return {}
        return{}

    def onchange_sap_number(self,cr,uid,ids,emp_id):
        sap_list = []
        emp_obj = self.pool.get('hr.employee')
        store_obj = self.pool.get('sap.store')
        dealer_obj = self.pool.get('dealer.class')
        sap_tracker_obj = self.pool.get('sap.tracker')
        mkt_tracker_obj = self.pool.get('market.tracker')
        #cr.execute('select store_id from hr_id_store_id where hr_id=%s',(emp_id,))
        #store_ids = map(lambda x: x[0], cr.fetchall())
        emp_data = emp_obj.browse(cr,uid,emp_id)
        date = datetime.datetime.now(pytz.timezone('US/Mountain')).date()
        if emp_data:
            dsr_store_id = emp_data.store_id.id
            store_type = emp_data.store_id.store_classification.id
            dsr_market_id = emp_data.store_id.market_id.id
            dsr_region_id = emp_data.store_id.market_id.region_market_id.id
            dealer_ids = dealer_obj.search(cr, uid, [('end_date','>=',date),('start_date','<=',date),('dealer_id','=',emp_id)])
            if dealer_ids:
                dealer_data = dealer_obj.browse(cr, uid, dealer_ids[0])
                dsr_store_data = dealer_data.store_name
                dsr_store_id = dsr_store_data.id
                store_type = dsr_store_data.store_classification.id
                dsr_market_id = dsr_store_data.market_id.id
                dsr_region_id = dsr_store_data.market_id.region_market_id.id
            sap_tracker_ids = sap_tracker_obj.search(cr, uid, [('end_date','>=',date),('start_date','<=',date),('sap_id','=',dsr_store_id),('store_inactive','=',False)])
            if sap_tracker_ids:
                sap_tracker_data = sap_tracker_obj.browse(cr, uid, sap_tracker_ids[0])
                dsr_market_id = sap_tracker_data.market_id.id
            mkt_tracker_ids = mkt_tracker_obj.search(cr, uid, [('end_date','>=',date),('start_date','<=',date),('market_id','=',dsr_market_id)])
            if mkt_tracker_ids:
                mkt_tracker_data = mkt_tracker_obj.browse(cr, uid, mkt_tracker_ids[0])
                dsr_region_id = mkt_tracker_data.region_market_id.id
            return {'value': {'dsr_store_id':dsr_store_id,'dsr_store_type':store_type,'dsr_market_id':dsr_market_id,'dsr_region_id' : dsr_region_id}}
        return {'value':{'dsr_store_id':False,'dsr_store_type':False,'dsr_market_id':False,'dsr_region_id':False}}

    def default_get(self, cr, uid, fields, context=None):
        res = super(wireless_dsr, self).default_get(cr, uid, fields, context=context)
        hr_obj = self.pool.get('hr.employee')
        dealer_obj = self.pool.get('dealer.class')
        des_obj = self.pool.get('designation.tracker')
        dealer_code = ''
        date = datetime.datetime.now(pytz.timezone('US/Mountain')).date()
        emp_id = hr_obj.search(cr, uid, [('user_id','=',context.get('uid') or uid)])
        if emp_id:
            ######## Getting dealer code from HR one2many ##################
            dealer_ids = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',date),('end_date','>=',date)])
            if dealer_ids:
                dealer_code = dealer_obj.browse(cr, uid, dealer_ids[0]).name
            ######## Browse Employee Data ######################
            emp_data = hr_obj.browse(cr, uid, emp_id[0], context=None)
            dsr_designation_id = emp_data.job_id.id
            des_ids = des_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',date),('end_date','>=',date)])
            if des_ids:
                dsr_designation_id = des_obj.browse(cr, uid, des_ids[0]).designation_id.id
            res.update({'dsr_dealer_code':dealer_code or False,
                        'dsr_sales_employee_id':emp_id[0],
                        'dsr_designation_id':dsr_designation_id
                        })
            vals= self.onchange_sap_number(cr,uid,1,emp_id[0])
            if vals:
                res.update(vals['value'])
        return res

# ****************** Onchange of Employee values get of dealer code, store, market, region, designation *********************** #
    def onchange_emp(self, cr, uid, ids, emp_id,dsr_date):
        hr_obj = self.pool.get('hr.employee')
        dealer_obj = self.pool.get('dealer.class')
        sap_tracker_obj = self.pool.get('sap.tracker')
        mkt_tracker_obj = self.pool.get('market.tracker')
        des_obj = self.pool.get('designation.tracker')
        dealer_code = ''
        if emp_id:
            hr_data = hr_obj.browse(cr, uid, emp_id)
            designation_id = hr_data.job_id.id
            dsr_store_id = hr_data.user_id.sap_id.id
            store_type = hr_data.user_id.sap_id.store_classification.id
            dsr_market_id = hr_data.user_id.market_id.id
            dsr_region_id = hr_data.user_id.region_id.id
            dealer_code_ids = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',dsr_date),('end_date','>=',dsr_date)])
            if dealer_code_ids:
                dealer_data = dealer_obj.browse(cr, uid, dealer_code_ids[0])
                dealer_code = dealer_data.name
                dsr_store_data = dealer_data.store_name
                dsr_store_id = dsr_store_data.id
                store_type = dsr_store_data.store_classification.id
                dsr_market_id = dsr_store_data.market_id.id
                dsr_region_id = dsr_store_data.market_id.region_market_id.id
            sap_tracker_ids = sap_tracker_obj.search(cr, uid, [('end_date','>=',dsr_date),('start_date','<=',dsr_date),('sap_id','=',dsr_store_id),('store_inactive','=',False)])
            if sap_tracker_ids:
                sap_tracker_data = sap_tracker_obj.browse(cr, uid, sap_tracker_ids[0])
                dsr_market_id = sap_tracker_data.market_id.id
            mkt_tracker_ids = mkt_tracker_obj.search(cr, uid, [('end_date','>=',dsr_date),('start_date','<=',dsr_date),('market_id','=',dsr_market_id)])
            if mkt_tracker_ids:
                mkt_tracker_data = mkt_tracker_obj.browse(cr, uid, mkt_tracker_ids[0])
                dsr_region_id = mkt_tracker_data.region_market_id.id
            des_ids = des_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',dsr_date),('end_date','>=',dsr_date)])
            if des_ids:
                designation_id = des_obj.browse(cr, uid, des_ids[0]).designation_id.id
            return {'value': {'dsr_dealer_code':dealer_code,
                            'dsr_designation_id':designation_id,
                            'dsr_store_type':store_type,
                            'dsr_store_id':dsr_store_id,
                            'dsr_market_id':dsr_market_id,
                            'dsr_region_id' : dsr_region_id}}
        return {}

    def onchange_date(self, cr, uid, ids, dsr_date, emp_id):
        hr_obj = self.pool.get('hr.employee')
        dealer_obj = self.pool.get('dealer.class')
        sap_tracker_obj = self.pool.get('sap.tracker')
        mkt_tracker_obj = self.pool.get('market.tracker')
        des_obj = self.pool.get('designation.tracker')
        dealer_code = ''
        if emp_id:
            hr_data = hr_obj.browse(cr, uid, emp_id)
            designation_id = hr_data.job_id.id
            dsr_store_id = hr_data.user_id.sap_id.id
            store_type = hr_data.user_id.sap_id.store_classification.id
            dsr_market_id = hr_data.user_id.market_id.id
            dsr_region_id = hr_data.user_id.region_id.id
            dealer_code_ids = dealer_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',dsr_date),('end_date','>=',dsr_date)])
            if dealer_code_ids:
                dealer_data = dealer_obj.browse(cr, uid, dealer_code_ids[0])
                dealer_code = dealer_data.name
                dsr_store_data = dealer_data.store_name
                dsr_store_id = dsr_store_data.id
                store_type = dsr_store_data.store_classification.id
                dsr_market_id = dsr_store_data.market_id.id
                dsr_region_id = dsr_store_data.market_id.region_market_id.id
            sap_tracker_ids = sap_tracker_obj.search(cr, uid, [('end_date','>=',dsr_date),('start_date','<=',dsr_date),('sap_id','=',dsr_store_id),('store_inactive','=',False)])
            if sap_tracker_ids:
                sap_tracker_data = sap_tracker_obj.browse(cr, uid, sap_tracker_ids[0])
                dsr_market_id = sap_tracker_data.market_id.id
            mkt_tracker_ids = mkt_tracker_obj.search(cr, uid, [('end_date','>=',dsr_date),('start_date','<=',dsr_date),('market_id','=',dsr_market_id)])
            if mkt_tracker_ids:
                mkt_tracker_data = mkt_tracker_obj.browse(cr, uid, mkt_tracker_ids[0])
                dsr_region_id = mkt_tracker_data.region_market_id.id
            des_ids = des_obj.search(cr, uid, [('dealer_id','=',emp_id),('start_date','<=',dsr_date),('end_date','>=',dsr_date)])
            if des_ids:
                designation_id = des_obj.browse(cr, uid, des_ids[0]).designation_id.id
            return {'value': {'dsr_dealer_code':dealer_code,
                            'dsr_designation_id':designation_id,
                            'dsr_store_type':store_type,
                            'dsr_store_id':dsr_store_id,
                            'dsr_market_id':dsr_market_id,
                            'dsr_region_id' : dsr_region_id}}
        return {}

    def validation_check(self, cr, uid, ids):
        uid = 1
        dsr_data = self.browse(cr, uid, ids[0])
        pos_obj = self.pool.get('wireless.dsr.postpaid.line')
        pre_obj = self.pool.get('wireless.dsr.prepaid.line')
        upg_obj = self.pool.get('wireless.dsr.upgrade.line')
        feature_obj = self.pool.get('wireless.dsr.feature.line')
        postpaid_line_data = dsr_data.postpaid_product_line
        prepaid_line_data = pre_obj.search(cr, uid, [('product_id','=',ids[0])])
        feature_line_data = feature_obj.search(cr, uid, [('feature_product_id','=',ids[0])])
        upgrade_line_data = dsr_data.upgrade_product_line
        dsr_current_date = dsr_data.dsr_date
        dsr_current_date = datetime.datetime.strptime(dsr_current_date, '%Y-%m-%d')
        valid_month = dsr_current_date.strftime('%m')
        valid_year = dsr_current_date.strftime('%Y')
        valid_date = (dsr_current_date - relativedelta(days=60))
        if prepaid_line_data:
            for prepaid_line_id in pre_obj.browse(cr, uid, prepaid_line_data):
                phone = prepaid_line_id.dsr_phone_no
                number = prepaid_line_id.dsr_imei_no
                card_number = prepaid_line_id.dsr_sim_no
                soc_code = prepaid_line_id.dsr_product_description.id
                prepaid_id = prepaid_line_id.id
                is_act = prepaid_line_id.is_act
                if phone:    
                    if is_act:
                        #search_phone_ids = pre_obj.search(cr, uid, [('dsr_phone_no','=',phone),('is_act','=',is_act),('state','=','done'),('dsr_exception','=',False),('id','!=',prepaid_id)])
                        cr.execute('''select id from wireless_dsr_prepaid_line where dsr_phone_no=%s and is_act=%s 
                            and state='done' and (dsr_exception=false or dsr_exception is null) and id!=%s''',(phone,is_act,prepaid_id))
                        search_phone_ids = map(lambda x: x[0], cr.fetchall())
                        if search_phone_ids:
                            for search_phone_pre_data in pre_obj.browse(cr, uid, search_phone_ids):
                                compare_date = search_phone_pre_data.product_id.dsr_date
                                ds = datetime.datetime.strptime(compare_date,'%Y-%m-%d')
                                search_mon = ds.strftime('%m')
                                search_year = ds.strftime('%Y')
                                if valid_month == search_mon and valid_year == search_year:
                                    raise osv.except_osv(_('Warning'),_("Prepaid mobile # %s found similar in Prepaid records within current month."%(phone)))
                    else:    
                        #search_phone_feature_ids = pre_obj.search(cr, uid, [('dsr_phone_no','=',phone),('dsr_product_description','=',soc_code),('is_act','=',is_act),('state','=','done'),('dsr_exception','=',False),('id','!=',prepaid_id)])
                        cr.execute('''select id from wireless_dsr_prepaid_line where dsr_phone_no=%s and dsr_product_description=%s and is_act=%s 
                            and state='done' and (dsr_exception=false or dsr_exception is null) and id!=%s''',(phone,soc_code,is_act,prepaid_id))
                        search_phone_feature_ids = map(lambda x: x[0], cr.fetchall())
                        if search_phone_feature_ids:
                            for search_phone_pre_data in pre_obj.browse(cr, uid, search_phone_feature_ids):
                                compare_date = search_phone_pre_data.product_id.dsr_date
                                ds = datetime.datetime.strptime(compare_date,'%Y-%m-%d')
                                search_mon = ds.strftime('%m')
                                search_year = ds.strftime('%Y')
                                if valid_month == search_mon and valid_year == search_year:
                                    raise osv.except_osv(_('Warning'),_("Similar Prepaid feature with this mobile # %s found in Prepaid records within current month."%(phone)))
                    #search_pos_phone_ids = pos_obj.search(cr, uid, [('dsr_phone_no','=',phone),('dsr_exception','=',False),('state','=','done')])
                    cr.execute('''select id from wireless_dsr_postpaid_line where dsr_phone_no=%s 
                             and (dsr_exception=false or dsr_exception is null) and state='done' ''',(phone,))
                    search_pos_phone_ids = map(lambda x: x[0], cr.fetchall())
                    #search_upg_phone_ids = upg_obj.search(cr, uid, [('dsr_phone_no','=',phone),('dsr_exception','=',False),('state','=','done')])
                    cr.execute('''select id from wireless_dsr_upgrade_line where dsr_phone_no=%s 
                             and (dsr_exception=false or dsr_exception is null) and state='done' ''',(phone,))
                    search_upg_phone_ids = map(lambda x: x[0], cr.fetchall())                    
                    if search_pos_phone_ids:
                        for search_pos_phone_data in pos_obj.browse(cr, uid, search_pos_phone_ids):
                            dsr_date = search_pos_phone_data.product_id.dsr_date
                            ds = datetime.datetime.strptime(dsr_date,'%Y-%m-%d')
                            search_mon = ds.strftime('%m')
                            search_year = ds.strftime('%Y')
                            if valid_month == search_mon and valid_year == search_year:
                                raise osv.except_osv(_('Warning'),_("Prepaid Phone # %s found similar in Postpaid records within current month."%(phone)))
                    if search_upg_phone_ids:
                        for search_upg_phone_data in upg_obj.browse(cr, uid, search_upg_phone_ids):
                            dsr_date = search_upg_phone_data.product_id.dsr_date
                            ds = datetime.datetime.strptime(dsr_date,'%Y-%m-%d')
                            search_mon = ds.strftime('%m')
                            search_year = ds.strftime('%Y')
                            if valid_month == search_mon and valid_year == search_year:
                                raise osv.except_osv(_('Warning'),_("Prepaid Phone # %s found similar in Upgrade records within current month."%(phone)))
                if number:    
                    if is_act:
                        #search_imei_ids = pre_obj.search(cr, uid, [('dsr_imei_no','=',number),('is_act','=',is_act),('state','=','done'),('dsr_exception','=',False),('id','!=',prepaid_id)])
                        cr.execute('''select id from wireless_dsr_prepaid_line where dsr_imei_no=%s and is_act=%s
                             and state='done' and (dsr_exception=false or dsr_exception is null) and id!=%s''',(number,is_act,prepaid_id))
                        search_imei_ids = map(lambda x: x[0], cr.fetchall())
                        if search_imei_ids:
                            for search_imei_pre_data in pre_obj.browse(cr, uid, search_imei_ids):
                                compare_date = search_imei_pre_data.product_id.dsr_date
                                ds = datetime.datetime.strptime(compare_date,'%Y-%m-%d')
                                search_mon = ds.strftime('%m')
                                search_year = ds.strftime('%Y')
                                if valid_month == search_mon and valid_year == search_year:
                                    raise osv.except_osv(_('Warning'),_("Prepaid IMEI # %s found similar in Prepaid records within current month."%(number)))
                    else:
                        #search_imei_feature_ids = pre_obj.search(cr, uid, [('dsr_imei_no','=',number),('dsr_product_description','=',soc_code),('is_act','=',is_act),('state','=','done'),('dsr_exception','=',False),('id','!=',prepaid_id)])
                        cr.execute('''select id from wireless_dsr_prepaid_line where dsr_imei_no=%s and dsr_product_description=%s and is_act=%s 
                            and state='done' and (dsr_exception=false or dsr_exception is null) and id!=%s''',(number,soc_code,is_act,prepaid_id))
                        search_imei_feature_ids = map(lambda x: x[0], cr.fetchall())
                        if search_imei_feature_ids:
                            for search_imei_pre_data in pre_obj.browse(cr, uid, search_imei_feature_ids):
                                compare_date = search_imei_pre_data.product_id.dsr_date
                                ds = datetime.datetime.strptime(compare_date,'%Y-%m-%d')
                                search_mon = ds.strftime('%m')
                                search_year = ds.strftime('%Y')
                                if valid_month == search_mon and valid_year == search_year:
                                    raise osv.except_osv(_('Warning'),_("Similar Prepaid Feature with this IMEI # %s found in Prepaid records within current month."%(number)))
                    #search_pos_imei_ids = pos_obj.search(cr, uid, [('dsr_imei_no','=',number),('state','=','done'),('dsr_exception','=',False)])
                    cr.execute('''select id from wireless_dsr_postpaid_line where dsr_imei_no=%s and state='done' and (dsr_exception=false or dsr_exception is null)''',(number,))
                    search_pos_imei_ids = map(lambda x: x[0], cr.fetchall())
                    #search_upg_imei_ids = upg_obj.search(cr, uid, [('dsr_imei_no','=',number),('state','=','done'),('dsr_exception','=',False)])
                    cr.execute('''select id from wireless_dsr_upgrade_line where dsr_imei_no=%s and state='done' and (dsr_exception=false or dsr_exception is null)''',(number,))
                    search_upg_imei_ids = map(lambda x: x[0], cr.fetchall())
                    if search_pos_imei_ids:
                        for search_pos_imei_data in pos_obj.browse(cr, uid, search_pos_imei_ids):
                            dsr_date = search_pos_imei_data.product_id.dsr_date
                            ds = datetime.datetime.strptime(dsr_date,'%Y-%m-%d')
                            search_mon = ds.strftime('%m')
                            search_year = ds.strftime('%Y')
                            if valid_month == search_mon and valid_year == search_year:
                                raise osv.except_osv(_('Warning'),_("Prepaid IMEI # %s found similar in Postpaid records within current month."%(number)))
                    if search_upg_imei_ids:
                        for search_upg_imei_data in upg_obj.browse(cr, uid, search_upg_imei_ids):
                            dsr_date = search_upg_imei_data.product_id.dsr_date
                            ds = datetime.datetime.strptime(dsr_date,'%Y-%m-%d')
                            search_mon = ds.strftime('%m')
                            search_year = ds.strftime('%Y')
                            if valid_month == search_mon and valid_year == search_year:
                                raise osv.except_osv(_('Warning'),_("Prepaid IMEI # %s found similar in Upgrade records within current month."%(number)))
                if card_number:    
                    if is_act:
                        #search_sim_ids = pre_obj.search(cr, uid, [('dsr_sim_no','=',card_number),('is_act','=',is_act),('state','=','done'),('dsr_exception','=',False),('id','!=',prepaid_id)])
                        cr.execute('''select id from wireless_dsr_prepaid_line where dsr_sim_no=%s and is_act=%s and state='done' and (dsr_exception=false or dsr_exception is null) and id!=%s''',(card_number,is_act,prepaid_id))
                        search_sim_ids = map(lambda x: x[0], cr.fetchall())
                        if search_sim_ids:
                            for search_sim_pre_data in pre_obj.browse(cr, uid, search_sim_ids):
                                compare_date = search_sim_pre_data.product_id.dsr_date
                                ds = datetime.datetime.strptime(compare_date,'%Y-%m-%d')
                                search_mon = ds.strftime('%m')
                                search_year = ds.strftime('%Y')
                                if valid_month == search_mon and valid_year == search_year:
                                    raise osv.except_osv(_('Warning'),_("Prepaid SIM # %s found similar in Prepaid records within current month."%(card_number)))
                    else:
                        #search_sim_feature_ids = pre_obj.search(cr, uid, [('dsr_sim_no','=',card_number),('dsr_product_description','=',soc_code),('is_act','=',is_act),('state','=','done'),('dsr_exception','=',False),('id','!=',prepaid_id)])
                        cr.execute('''select id from wireless_dsr_prepaid_line where dsr_sim_no=%s and dsr_product_description=%s and is_act=%s and state='done' and (dsr_exception=false or dsr_exception is null) and id!=%s''',(card_number,soc_code,is_act,prepaid_id))
                        search_sim_feature_ids = map(lambda x: x[0], cr.fetchall())
                        if search_sim_feature_ids:
                            for search_sim_pre_data in pre_obj.browse(cr, uid, search_sim_feature_ids):
                                compare_date = search_sim_pre_data.product_id.dsr_date
                                ds = datetime.datetime.strptime(compare_date,'%Y-%m-%d')
                                search_mon = ds.strftime('%m')
                                search_year = ds.strftime('%Y')
                                if valid_month == search_mon and valid_year == search_year:
                                    raise osv.except_osv(_('Warning'),_("Similar Prepaid Feature with this SIM # %s found in Prepaid records within current month."%(card_number)))
                    #search_pos_sim_ids = pos_obj.search(cr, uid, [('dsr_sim_no','=',card_number),('state','=','done'),('dsr_exception','=',False)])
                    cr.execute('''select id from wireless_dsr_postpaid_line where dsr_sim_no=%s and state='done' and (dsr_exception=false or dsr_exception is null)''',(card_number,))
                    search_pos_sim_ids = map(lambda x: x[0], cr.fetchall())
                    #search_upg_sim_ids = upg_obj.search(cr, uid, [('dsr_sim_no','=',card_number),('state','=','done'),('dsr_exception','=',False)]) 
                    cr.execute('''select id from wireless_dsr_upgrade_line where dsr_sim_no=%s and state='done' and (dsr_exception=false or dsr_exception is null)''',(card_number,))
                    search_upg_sim_ids = map(lambda x: x[0], cr.fetchall())                   
                    if search_pos_sim_ids:
                        for search_pos_sim_data in pos_obj.browse(cr, uid, search_pos_sim_ids):
                            dsr_date = search_pos_sim_data.product_id.dsr_date
                            ds = datetime.datetime.strptime(dsr_date,'%Y-%m-%d')
                            search_mon = ds.strftime('%m')
                            search_year = ds.strftime('%Y')
                            if valid_month == search_mon and valid_year == search_year:
                                raise osv.except_osv(_('Warning'),_("Prepaid SIM # %s found similar in Postpaid records within current month."%(card_number)))
                    if search_upg_sim_ids:
                        for search_upg_sim_data in upg_obj.browse(cr, uid, search_upg_sim_ids):
                            dsr_date = search_upg_sim_data.product_id.dsr_date
                            ds = datetime.datetime.strptime(dsr_date,'%Y-%m-%d')
                            search_mon = ds.strftime('%m')
                            search_year = ds.strftime('%Y')
                            if valid_month == search_mon and valid_year == search_year:
                                raise osv.except_osv(_('Warning'),_("Prepaid SIM # %s found similar in Upgrade records within current month."%(card_number)))
        if upgrade_line_data:
            for upgrade_line_id in upgrade_line_data:
                phone = upgrade_line_id.dsr_phone_no
                sim = upgrade_line_id.dsr_sim_no
                imei = upgrade_line_id.dsr_imei_no
                upgrade_id = upgrade_line_id.id
                if phone:
                    #postpaid_search_ids = pos_obj.search(cr, uid, [('dsr_phone_no','=',phone),('state','=','done'),('dsr_exception','=',False)])
                    cr.execute('''select id from wireless_dsr_postpaid_line where dsr_phone_no=%s and state='done' and (dsr_exception=false or dsr_exception is null)''',(phone,))
                    postpaid_search_ids = map(lambda x: x[0], cr.fetchall()) 
                    #pre_phone_search_ids = pre_obj.search(cr, uid, [('dsr_phone_no','=',phone),('state','=','done'),('dsr_exception','=',False),('created_feature','=',False)])
                    cr.execute('''select id from wireless_dsr_prepaid_line where dsr_phone_no=%s and state='done' and (dsr_exception=false or dsr_exception is null) and (created_feature=false or created_feature is null)''',(phone,))
                    pre_phone_search_ids = map(lambda x: x[0], cr.fetchall())
                    #upg_phone_search_ids = upg_obj.search(cr, uid, [('dsr_phone_no','=',phone),('state','=','done'),('dsr_exception','=',False),('id','!=',upgrade_id)])
                    cr.execute('''select id from wireless_dsr_upgrade_line where dsr_phone_no=%s and state='done' and (dsr_exception=false or dsr_exception is null) and id!=%s''',(phone,upgrade_id))
                    upg_phone_search_ids = map(lambda x: x[0], cr.fetchall())
                    if postpaid_search_ids:
                        for pos_search_data in pos_obj.browse(cr, uid, postpaid_search_ids):
                            dsr_date = pos_search_data.product_id.dsr_date
                            ds = datetime.datetime.strptime(dsr_date,'%Y-%m-%d')
                            search_mon = ds.strftime('%m')
                            search_year = ds.strftime('%Y')
                            if valid_month == search_mon and valid_year == search_year:
                                raise osv.except_osv(_('Warning'),_("Upgrade Phone # %s activation is done within same calendar month."%(phone)))
                    if pre_phone_search_ids:
                        for pre_phone_search_data in pre_obj.browse(cr, uid, pre_phone_search_ids):
                            dsr_date = pre_phone_search_data.product_id.dsr_date
                            ds = datetime.datetime.strptime(dsr_date,'%Y-%m-%d')
                            search_mon = ds.strftime('%m')
                            search_year = ds.strftime('%Y')
                            if valid_month == search_mon and valid_year == search_year:
                                raise osv.except_osv(_('Warning'),_("Upgrade Phone # %s found similar in Prepaid in same calendar month."%(phone)))
                    if upg_phone_search_ids:
                        for upg_phone_search_data in upg_obj.browse(cr, uid, upg_phone_search_ids):
                            dsr_date = upg_phone_search_data.product_id.dsr_date
                            ds = datetime.datetime.strptime(dsr_date,'%Y-%m-%d')
                            search_mon = ds.strftime('%m')
                            search_year = ds.strftime('%Y')
                            if valid_month == search_mon and valid_year == search_year:
                                raise osv.except_osv(_('Warning'),_("Upgrade Phone # %s found similar in Upgrade in same calendar month."%(phone)))
                if sim:
                    #pos_search_ids = pos_obj.search(cr, uid, [('dsr_sim_no','=',sim),('state','=','done'),('dsr_exception','=',False)])
                    cr.execute('''select id from wireless_dsr_postpaid_line where dsr_sim_no=%s and state='done' and (dsr_exception=false or dsr_exception is null)''',(sim,))
                    pos_search_ids = map(lambda x: x[0], cr.fetchall())
                    #pre_sim_search_ids = pre_obj.search(cr, uid, [('dsr_sim_no','=',sim),('state','=','done'),('dsr_exception','=',False),('created_feature','=',False)])
                    cr.execute('''select id from wireless_dsr_prepaid_line where dsr_sim_no=%s and state='done' and (dsr_exception=false or dsr_exception is null) and (created_feature=false or created_feature is null)''',(sim,))
                    pre_sim_search_ids = map(lambda x: x[0], cr.fetchall())
                    #upg_sim_search_ids = upg_obj.search(cr, uid, [('dsr_sim_no','=',sim),('state','=','done'),('dsr_exception','=',False),('id','!=',upgrade_id)])
                    cr.execute('''select id from wireless_dsr_upgrade_line where dsr_sim_no=%s and state='done' and (dsr_exception=false or dsr_exception is null) and id!=%s''',(sim,upgrade_id))
                    upg_sim_search_ids = map(lambda x: x[0], cr.fetchall())
                    if pos_search_ids:
                        for pos_search_data in pos_obj.browse(cr, uid, pos_search_ids):
                            dsr_date = pos_search_data.product_id.dsr_date
                            ds = datetime.datetime.strptime(dsr_date,'%Y-%m-%d')
                            search_mon = ds.strftime('%m')
                            search_year = ds.strftime('%Y')
                            if valid_month == search_mon and valid_year == search_year:
                                raise osv.except_osv(_('Warning'),_("Upgrade SIM # %s activation is done within same calendar month."%(sim)))
                    if pre_sim_search_ids:
                        for pre_sim_search_data in pre_obj.browse(cr, uid, pre_sim_search_ids):
                            dsr_date = pre_sim_search_data.product_id.dsr_date
                            ds = datetime.datetime.strptime(dsr_date,'%Y-%m-%d')
                            search_mon = ds.strftime('%m')
                            search_year = ds.strftime('%Y')
                            if valid_month == search_mon and valid_year == search_year:
                                raise osv.except_osv(_('Warning'),_("Upgrade SIM # %s found similar in Prepaid in same calendar month."%(sim)))
                    if upg_sim_search_ids:
                        for upg_sim_search_data in upg_obj.browse(cr, uid, upg_sim_search_ids):
                            dsr_date = upg_sim_search_data.product_id.dsr_date
                            ds = datetime.datetime.strptime(dsr_date,'%Y-%m-%d')
                            search_mon = ds.strftime('%m')
                            search_year = ds.strftime('%Y')
                            if valid_month == search_mon and valid_year == search_year:
                                raise osv.except_osv(_('Warning'),_("Upgrade SIM # %s found similar in Upgrade records in same calendar month."%(sim)))
                if imei:
                    #pos_search_ids = pos_obj.search(cr, uid, [('dsr_imei_no','=',imei),('state','=','done'),('dsr_exception','=',False)])
                    cr.execute('''select id from wireless_dsr_postpaid_line where dsr_imei_no=%s and state='done' and (dsr_exception=false or dsr_exception is null)''',(imei,))
                    pos_search_ids = map(lambda x: x[0], cr.fetchall())
                    #pre_imei_search_ids = pre_obj.search(cr, uid, [('dsr_imei_no','=',imei),('state','=','done'),('dsr_exception','=',False),('created_feature','=',False)])
                    cr.execute('''select id from wireless_dsr_prepaid_line where dsr_imei_no=%s and state='done' and (dsr_exception=false or dsr_exception is null) and (created_feature=false or created_feature is null)''',(imei,))
                    pre_imei_search_ids = map(lambda x: x[0], cr.fetchall())
                    #upg_imei_search_ids = upg_obj.search(cr, uid, [('dsr_imei_no','=',imei),('state','=','done'),('dsr_exception','=',False),('id','!=',upgrade_id)])
                    cr.execute('''select id from wireless_dsr_upgrade_line where dsr_imei_no=%s and state='done' and (dsr_exception=false or dsr_exception is null) and id!=%s''',(imei,upgrade_id))
                    upg_imei_search_ids = map(lambda x: x[0], cr.fetchall())
                    if pos_search_ids:
                        for pos_search_data in pos_obj.browse(cr, uid, pos_search_ids):
                            dsr_date = pos_search_data.product_id.dsr_date
                            compare_date = datetime.datetime.strptime(dsr_date,'%Y-%m-%d')
                            if compare_date > valid_date:
                                raise osv.except_osv(_('Warning'),_("Upgrade IMEI # %s activation is done within 60 days."%(imei)))
                    if pre_imei_search_ids:
                        for pre_imei_search_data in pre_obj.browse(cr, uid, pre_imei_search_ids):
                            dsr_date = pre_imei_search_data.product_id.dsr_date
                            ds = datetime.datetime.strptime(dsr_date,'%Y-%m-%d')
                            search_mon = ds.strftime('%m')
                            search_year = ds.strftime('%Y')
                            if valid_month == search_mon and valid_year == search_year:
                                raise osv.except_osv(_('Warning'),_("Upgrade IMEI # %s found similar in Prepaid in same calendar month."%(imei)))
                    if upg_imei_search_ids:
                        for upg_imei_search_data in upg_obj.browse(cr, uid, upg_imei_search_ids):
                            dsr_date = upg_imei_search_data.product_id.dsr_date
                            ds = datetime.datetime.strptime(dsr_date,'%Y-%m-%d')
                            search_mon = ds.strftime('%m')
                            search_year = ds.strftime('%Y')
                            if valid_month == search_mon and valid_year == search_year:
                                raise osv.except_osv(_('Warning'),_("Upgrade IMEI # %s found similar in Upgrade records in same calendar month."%(imei)))
        if postpaid_line_data:
            for postpaid_line_id in postpaid_line_data:
                phone = postpaid_line_id.dsr_phone_no
                number = postpaid_line_id.dsr_imei_no
                card_number = postpaid_line_id.dsr_sim_no
                postpaid_id = postpaid_line_id.id
                if phone:    
                    #search_phone_ids = pos_obj.search(cr, uid, [('dsr_phone_no','=',phone),('state','=','done'),('dsr_exception','=',False),('id','!=',postpaid_id)])
                    cr.execute('''select id from wireless_dsr_postpaid_line where dsr_phone_no=%s and state='done' and (dsr_exception=false or dsr_exception is null) and id!=%s''',(phone,postpaid_id))
                    search_phone_ids = map(lambda x: x[0], cr.fetchall())
                    #search_pre_phone_ids = pre_obj.search(cr, uid, [('dsr_phone_no','=',phone),('state','=','done'),('created_feature','=',False),('dsr_exception','=',False)])
                    cr.execute('''select id from wireless_dsr_prepaid_line where dsr_phone_no=%s and state='done' and (created_feature=false or created_feature is null) and (dsr_exception=false or dsr_exception is null)''',(phone,))
                    search_pre_phone_ids = map(lambda x: x[0], cr.fetchall())
                    #search_upg_phone_ids = upg_obj.search(cr, uid, [('dsr_phone_no','=',phone),('state','=','done'),('dsr_exception','=',False)])
                    cr.execute('''select id from wireless_dsr_upgrade_line where dsr_phone_no=%s and state='done' and (dsr_exception=false or dsr_exception is null)''',(phone,))
                    search_upg_phone_ids = map(lambda x: x[0], cr.fetchall())
                    if search_phone_ids:
                        for search_phone_pos_data in pos_obj.browse(cr, uid, search_phone_ids):
                            compare_date = search_phone_pos_data.product_id.dsr_date
                            compare_date = datetime.datetime.strptime(compare_date, '%Y-%m-%d')
                            if compare_date > valid_date:
                                raise osv.except_osv(_('Warning'),_("Postpaid Phone # %s found similar in Postpaid records within 60 days."%(phone)))
                    if search_pre_phone_ids:
                        for search_pre_phone_data in pre_obj.browse(cr, uid, search_pre_phone_ids):
                            dsr_date = search_pre_phone_data.product_id.dsr_date
                            ds = datetime.datetime.strptime(dsr_date,'%Y-%m-%d')
                            search_mon = ds.strftime('%m')
                            search_year = ds.strftime('%Y')
                            if valid_month == search_mon and valid_year == search_year:
                                raise osv.except_osv(_('Warning'),_("Postpaid Phone # %s found similar in Prepaid in same calendar month."%(phone)))
                    if search_upg_phone_ids:
                        for search_upg_phone_data in upg_obj.browse(cr, uid, search_upg_phone_ids):
                            compare_date = search_upg_phone_data.product_id.dsr_date
                            compare_date = datetime.datetime.strptime(compare_date, '%Y-%m-%d')
                            if compare_date > valid_date:
                                raise osv.except_osv(_('Warning'),_("Postpaid Phone # %s found similar in Upgrade records within 60 days."%(phone)))
                if number:    
                    #search_imei_ids = pos_obj.search(cr, uid, [('dsr_imei_no','=',number),('state','=','done'),('dsr_exception','=',False),('id','!=',postpaid_id)])
                    cr.execute('''select id from wireless_dsr_postpaid_line where dsr_imei_no=%s and state='done' and (dsr_exception=false or dsr_exception is null) and id!=%s''',(number,postpaid_id))
                    search_imei_ids = map(lambda x: x[0], cr.fetchall())
                    #search_pre_imei_ids = pre_obj.search(cr, uid, [('dsr_imei_no','=',number),('state','=','done'),('dsr_exception','=',False),('created_feature','=',False)])
                    cr.execute('''select id from wireless_dsr_prepaid_line where dsr_imei_no=%s and state='done' and (dsr_exception=false or dsr_exception is null) and (created_feature=false or created_feature is null)''',(number,))
                    search_pre_imei_ids = map(lambda x: x[0], cr.fetchall())
                    #search_upg_imei_ids = upg_obj.search(cr, uid, [('dsr_imei_no','=',number),('state','=','done'),('dsr_exception','=',False)])
                    cr.execute('''select id from wireless_dsr_upgrade_line where dsr_imei_no=%s and state='done' and (dsr_exception=false or dsr_exception is null)''',(number,))
                    search_upg_imei_ids = map(lambda x: x[0], cr.fetchall())
                    if search_imei_ids:
                        for search_imei_pos_data in pos_obj.browse(cr, uid, search_imei_ids):
                            compare_date = search_imei_pos_data.product_id.dsr_date
                            compare_date = datetime.datetime.strptime(compare_date, '%Y-%m-%d')
                            if compare_date > valid_date:
                                raise osv.except_osv(_('Warning'),_("Postpaid IMEI # %s found similar in Postpaid records within 60 days."%(number)))
                    if search_pre_imei_ids:
                        for search_pre_imei_data in pre_obj.browse(cr, uid, search_pre_imei_ids):
                            dsr_date = search_pre_imei_data.product_id.dsr_date
                            ds = datetime.datetime.strptime(dsr_date,'%Y-%m-%d')
                            search_mon = ds.strftime('%m')
                            search_year = ds.strftime('%Y')
                            if valid_month == search_mon and valid_year == search_year:
                                raise osv.except_osv(_('Warning'),_("Postpaid IMEI # %s found similar in Prepaid in same calendar month."%(number)))
                    if search_upg_imei_ids:
                        for search_imei_upg_data in upg_obj.browse(cr, uid, search_upg_imei_ids):
                            compare_date = search_imei_upg_data.product_id.dsr_date
                            compare_date = datetime.datetime.strptime(compare_date, '%Y-%m-%d')
                            if compare_date > valid_date:
                                raise osv.except_osv(_('Warning'),_("Postpaid IMEI # %s found similar in Upgrade records within 60 days."%(number)))
                if card_number:    
                    #search_sim_ids = pos_obj.search(cr, uid, [('dsr_sim_no','=',card_number),('state','=','done'),('dsr_exception','=',False),('id','!=',postpaid_id)])
                    cr.execute('''select id from wireless_dsr_postpaid_line where dsr_sim_no=%s and state='done' and (dsr_exception=false or dsr_exception is null) and id!=%s''',(card_number,postpaid_id))
                    search_sim_ids = map(lambda x: x[0], cr.fetchall())
                    #search_pre_sim_ids = pre_obj.search(cr, uid, [('dsr_sim_no','=',card_number),('state','=','done'),('dsr_exception','=',False),('created_feature','=',False)])
                    cr.execute('''select id from wireless_dsr_prepaid_line where dsr_sim_no=%s and state='done' and (dsr_exception=false or dsr_exception is null) and (created_feature=false or created_feature is null)''',(card_number,))
                    search_pre_sim_ids = map(lambda x: x[0], cr.fetchall())
                    #search_sim_upg_ids = upg_obj.search(cr, uid, [('dsr_sim_no','=',card_number),('state','=','done'),('dsr_exception','=',False)])
                    cr.execute('''select id from wireless_dsr_upgrade_line where dsr_sim_no=%s and state='done' and (dsr_exception=false or dsr_exception is null)''',(card_number,))
                    search_sim_upg_ids = map(lambda x: x[0], cr.fetchall())
                    if search_sim_ids:
                        for search_sim_pos_data in pos_obj.browse(cr, uid, search_sim_ids):
                            compare_date = search_sim_pos_data.product_id.dsr_date
                            compare_date = datetime.datetime.strptime(compare_date, '%Y-%m-%d')
                            if compare_date > valid_date:
                                raise osv.except_osv(_('Warning'),_("Postpaid SIM # %s found similar in Postpaid records within 60 days."%(card_number)))
                    if search_pre_sim_ids:
                        for search_pre_sim_data in pre_obj.browse(cr, uid, search_pre_sim_ids):
                            dsr_date = search_pre_sim_data.product_id.dsr_date
                            ds = datetime.datetime.strptime(dsr_date,'%Y-%m-%d')
                            search_mon = ds.strftime('%m')
                            search_year = ds.strftime('%Y')
                            if valid_month == search_mon and valid_year == search_year:
                                raise osv.except_osv(_('Warning'),_("Postpaid SIM # %s found similar in Prepaid in same calendar month."%(card_number)))
                    if search_sim_upg_ids:
                        for search_upg_sim_data in upg_obj.browse(cr, uid, search_sim_upg_ids):
                            compare_date = search_upg_sim_data.product_id.dsr_date
                            compare_date = datetime.datetime.strptime(compare_date, '%Y-%m-%d')
                            if compare_date > valid_date:
                                raise osv.except_osv(_('Warning'),_("Postpaid SIM # %s found similar in Upgrade records within 60 days."%(card_number)))
        if feature_line_data:
            for feature_line_id in feature_obj.browse(cr, uid, feature_line_data):
                phone = feature_line_id.dsr_phone_no
                number = feature_line_id.dsr_imei_no
                card_number = feature_line_id.dsr_sim_no
                prod_code = feature_line_id.dsr_product_code.id
                feature_id = feature_line_id.id
                if phone:    
                    #search_phone_ids = feature_obj.search(cr, uid, [('dsr_product_code','=',prod_code),('dsr_phone_no','=',phone),('state','=','done'),('dsr_exception','=',False),('id','!=',feature_id)])
                    cr.execute('''select id from wireless_dsr_feature_line where dsr_product_code=%s and dsr_phone_no=%s and state='done' and (dsr_exception=false or dsr_exception is null) and id!=%s''',(prod_code,phone,feature_id))
                    search_phone_ids = map(lambda x: x[0], cr.fetchall())
                    if search_phone_ids:
                        for search_phone_feature_data in feature_obj.browse(cr, uid, search_phone_ids):
                            compare_date = search_phone_feature_data.feature_product_id.dsr_date
                            compare_date = datetime.datetime.strptime(compare_date, '%Y-%m-%d')
                            if compare_date > valid_date:
                                raise osv.except_osv(_('Warning'),_("Similar mobile # %s with feature SOC Code found in Data Feature records within 60 days."%(phone)))
                if number:    
                    #search_imei_ids = feature_obj.search(cr, uid, [('dsr_product_code','=',prod_code),('dsr_imei_no','=',number),('state','=','done'),('dsr_exception','=',False),('id','!=',feature_id)])
                    cr.execute('''select id from wireless_dsr_feature_line where dsr_product_code=%s and dsr_imei_no=%s and state='done' and (dsr_exception=false or dsr_exception is null) and id!=%s''',(prod_code,number,feature_id))
                    search_imei_ids = map(lambda x: x[0], cr.fetchall())
                    if search_imei_ids:
                        for search_imei_feature_data in feature_obj.browse(cr, uid, search_imei_ids):
                            compare_date = search_imei_feature_data.feature_product_id.dsr_date
                            compare_date = datetime.datetime.strptime(compare_date, '%Y-%m-%d')
                            if compare_date > valid_date:
                                raise osv.except_osv(_('Warning'),_("Similar IMEI # %s with feature SOC Code found in Data Feature records within 60 days."%(number)))
                if card_number:    
                    #search_sim_ids = feature_obj.search(cr, uid, [('dsr_product_code','=',prod_code),('dsr_sim_no','=',card_number),('state','=','done'),('dsr_exception','=',False),('id','!=',feature_id)])
                    cr.execute('''select id from wireless_dsr_feature_line where dsr_product_code=%s and dsr_sim_no=%s and state='done' and (dsr_exception=false or dsr_exception is null) and id!=%s''',(prod_code,card_number,feature_id))
                    search_sim_ids = map(lambda x: x[0], cr.fetchall())
                    if search_sim_ids:
                        for search_sim_feature_data in feature_obj.browse(cr, uid, search_sim_ids):
                            compare_date = search_sim_feature_data.feature_product_id.dsr_date
                            compare_date = datetime.datetime.strptime(compare_date, '%Y-%m-%d')
                            if compare_date > valid_date:
                                raise osv.except_osv(_('Warning'),_("Similar SIM # %s with feature SOC Code found in Data Feature records within 60 days."%(card_number)))
        return True
    
    def validation_check_eip_warranty(self, cr, uid, ids):
        uid = 1
        pos_obj = self.pool.get('wireless.dsr.postpaid.line')
        feature_obj = self.pool.get('wireless.dsr.feature.line')
        upg_obj = self.pool.get('wireless.dsr.upgrade.line')
        feature_ids = feature_obj.search(cr, uid, [('feature_product_id','=',ids[0])])
        for feature_id in feature_ids:
            feature_data = feature_obj.browse(cr, uid, feature_id)
            is_php = feature_data.dsr_product_code.is_php
            is_jump = feature_data.dsr_product_code.is_jump
            upgrade_id = feature_data.upgrade_id.id
            postpaid_id = feature_data.postpaid_id.id
            if (not feature_data.dsr_warranty) and (is_jump or is_php) and (not upgrade_id) and (not postpaid_id):
                phone = feature_data.dsr_phone_no
                sim = feature_data.dsr_sim_no
                # imei = feature_data.dsr_imei_no
                # pos_search_ids = pos_obj.search(cr, uid, [('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
                #pos_search_ids = pos_obj.search(cr, uid, [('dsr_phone_no','=',phone),('dsr_sim_no','=',sim)])
                cr.execute('''select id from wireless_dsr_postpaid_line where dsr_sim_no=%s and dsr_phone_no=%s and dsr_imei_no=%s''',(sim,phone,imei))
                pos_search_ids = map(lambda x: x[0], cr.fetchall())
                #upg_search_ids = upg_obj.search(cr, uid, [('dsr_phone_no','=',phone),('dsr_sim_no','=',sim)])
                cr.execute('''select id from wireless_dsr_upgrade_line where dsr_sim_no=%s and dsr_phone_no=%s''',(sim,phone))
                upg_search_ids = map(lambda x: x[0], cr.fetchall())
                if pos_search_ids:
                    for pos_search_id in pos_search_ids:
                        pos_data = pos_obj.browse(cr, uid, pos_search_id)
                        pos_dsr_id = pos_data.product_id.id
                        pos_dsr_data = self.browse(cr, uid, pos_dsr_id)
                        pos_trans_date = pos_dsr_data.dsr_date
                        pos_trans_date = datetime.datetime.strptime(pos_trans_date, '%Y-%m-%d')
                        feature_trans_date = self.browse(cr, uid, ids[0]).dsr_date
                        feature_trans_date = datetime.datetime.strptime(feature_trans_date, '%Y-%m-%d')
                        max_date = (pos_trans_date + relativedelta(days=14))
                        if feature_trans_date > max_date or feature_trans_date < pos_trans_date:
                            raise osv.except_osv(('Warning'),("You can not enter JUMP for Phone # %s which has exceeded 14 days from activation."%(phone)))
                elif upg_search_ids:
                    for upg_search_id in upg_search_ids:
                        upg_data = upg_obj.browse(cr, uid, upg_search_id)
                        upg_dsr_id = upg_data.product_id.id
                        upg_dsr_data = self.browse(cr, uid, upg_dsr_id)
                        upg_trans_date = upg_dsr_data.dsr_date
                        upg_trans_date = datetime.datetime.strptime(upg_trans_date, '%Y-%m-%d')
                        feature_trans_date = self.browse(cr, uid, ids[0]).dsr_date
                        feature_trans_date = datetime.datetime.strptime(feature_trans_date, '%Y-%m-%d')
                        max_date = (upg_trans_date + relativedelta(days=14))
                        if feature_trans_date > max_date or feature_trans_date < upg_trans_date:
                            raise osv.except_osv(('Warning'),("You can not enter JUMP for Phone # %s which has exceeded 14 days from Upgrade."%(phone)))
        return True

    def check_same_number_write(self, cr, uid, ids, vals):
        pos_dsr_sim_no = []
        pos_dsr_imei_no = []
        pos_dsr_phone_no = []
        pre_dsr_sim_no = []
        pre_dsr_imei_no = []
        pre_dsr_phone_no = []
        upg_dsr_sim_no = []
        upg_dsr_imei_no = []
        upg_dsr_phone_no = []
        offer_dsr_imei_no = []
        dsr_data = self.browse(cr, uid, ids[0])
        postpaid_line_data = dsr_data.postpaid_product_line
        upgrade_line_data = dsr_data.upgrade_product_line
        prepaid_line_data = dsr_data.prepaid_product_line
        offer_line_data = dsr_data.dsr_offer_ids
        if 'postpaid_product_line' in vals:
            postpaid_product_line = vals['postpaid_product_line']
            for postpaid_product_line_id in postpaid_product_line:
                post_line_action = postpaid_product_line_id[0]
                post_line_id = postpaid_product_line_id[1]
                postpaid_product_line_id = postpaid_product_line_id[2]
                if post_line_action != 2:
                    if postpaid_product_line_id:
                        if 'dsr_sim_no' in postpaid_product_line_id:
                            pos_dsr_sim_no.append(postpaid_product_line_id['dsr_sim_no'])
                        else:
                            for postpaid_line_data_id in postpaid_line_data:
                                if postpaid_line_data_id.id == post_line_id:
                                    pos_dsr_sim_no.append(postpaid_line_data_id.dsr_sim_no)
                        if 'dsr_imei_no' in postpaid_product_line_id:
                            pos_dsr_imei_no.append(postpaid_product_line_id['dsr_imei_no'])
                        else:
                            for postpaid_line_data_id in postpaid_line_data:
                                if postpaid_line_data_id.id == post_line_id:
                                    pos_dsr_imei_no.append(postpaid_line_data_id.dsr_imei_no)
                        if 'dsr_phone_no' in postpaid_product_line_id:
                            pos_dsr_phone_no.append(postpaid_product_line_id['dsr_phone_no'])
                        else:
                            for postpaid_line_data_id in postpaid_line_data:
                                if postpaid_line_data_id.id == post_line_id:
                                    pos_dsr_phone_no.append(postpaid_line_data_id.dsr_phone_no)
                    else:
                        for postpaid_line_data_id in postpaid_line_data:
                            if postpaid_line_data_id.id == post_line_id:
                                pos_dsr_sim_no.append(postpaid_line_data_id.dsr_sim_no)
                                pos_dsr_imei_no.append(postpaid_line_data_id.dsr_imei_no)
                                pos_dsr_phone_no.append(postpaid_line_data_id.dsr_phone_no)
        else:
            for postpaid_line_data_id in postpaid_line_data:
                pos_dsr_sim_no.append(postpaid_line_data_id.dsr_sim_no)
                pos_dsr_imei_no.append(postpaid_line_data_id.dsr_imei_no)
                pos_dsr_phone_no.append(postpaid_line_data_id.dsr_phone_no)
        if 'prepaid_product_line' in vals:
            prepaid_product_line = vals['prepaid_product_line']
            for postpaid_product_line_id in prepaid_product_line:
                post_line_action = postpaid_product_line_id[0]
                post_line_id = postpaid_product_line_id[1]
                postpaid_product_line_id = postpaid_product_line_id[2]
                if post_line_action != 2:    
                    if postpaid_product_line_id:
                        if 'dsr_sim_no' in postpaid_product_line_id:
                            pre_dsr_sim_no.append(postpaid_product_line_id['dsr_sim_no'])
                        else:
                            for postpaid_line_data_id in prepaid_line_data:
                                if postpaid_line_data_id.id == post_line_id:
                                    pre_dsr_sim_no.append(postpaid_line_data_id.dsr_sim_no)
                        if 'dsr_imei_no' in postpaid_product_line_id:
                            pre_dsr_imei_no.append(postpaid_product_line_id['dsr_imei_no'])
                        else:
                            for postpaid_line_data_id in prepaid_line_data:
                                if postpaid_line_data_id.id == post_line_id:
                                    pre_dsr_imei_no.append(postpaid_line_data_id.dsr_imei_no)
                        if 'dsr_phone_no' in postpaid_product_line_id:
                            pre_dsr_phone_no.append(postpaid_product_line_id['dsr_phone_no'])
                        else:
                            for postpaid_line_data_id in prepaid_line_data:
                                if postpaid_line_data_id.id == post_line_id:
                                    pre_dsr_phone_no.append(postpaid_line_data_id.dsr_phone_no)
                    else:
                        for postpaid_line_data_id in prepaid_line_data:
                            if postpaid_line_data_id.id == post_line_id:
                                pre_dsr_sim_no.append(postpaid_line_data_id.dsr_sim_no)
                                pre_dsr_imei_no.append(postpaid_line_data_id.dsr_imei_no)
                                pre_dsr_phone_no.append(postpaid_line_data_id.dsr_phone_no)
        else:
            for postpaid_line_data_id in prepaid_line_data:
                pre_dsr_sim_no.append(postpaid_line_data_id.dsr_sim_no)
                pre_dsr_imei_no.append(postpaid_line_data_id.dsr_imei_no)
                pre_dsr_phone_no.append(postpaid_line_data_id.dsr_phone_no)
        if 'upgrade_product_line' in vals:
            upgrade_product_line = vals['upgrade_product_line']
            for postpaid_product_line_id in upgrade_product_line:
                post_line_action = postpaid_product_line_id[0]
                post_line_id = postpaid_product_line_id[1]
                postpaid_product_line_id = postpaid_product_line_id[2]
                if post_line_action != 2:    
                    if postpaid_product_line_id:
                        if 'dsr_sim_no' in postpaid_product_line_id:
                            upg_dsr_sim_no.append(postpaid_product_line_id['dsr_sim_no'])
                        else:
                            for postpaid_line_data_id in upgrade_line_data:
                                if postpaid_line_data_id.id == post_line_id:
                                    upg_dsr_sim_no.append(postpaid_line_data_id.dsr_sim_no)
                        if 'dsr_imei_no' in postpaid_product_line_id:
                            upg_dsr_imei_no.append(postpaid_product_line_id['dsr_imei_no'])
                        else:
                            for postpaid_line_data_id in upgrade_line_data:
                                if postpaid_line_data_id.id == post_line_id:
                                    upg_dsr_imei_no.append(postpaid_line_data_id.dsr_imei_no)
                        if 'dsr_phone_no' in postpaid_product_line_id:
                            upg_dsr_phone_no.append(postpaid_product_line_id['dsr_phone_no'])
                        else:
                            for postpaid_line_data_id in upgrade_line_data:
                                if postpaid_line_data_id.id == post_line_id:
                                    upg_dsr_phone_no.append(postpaid_line_data_id.dsr_phone_no)
                    else:
                        for postpaid_line_data_id in upgrade_line_data:
                            if postpaid_line_data_id.id == post_line_id:
                                upg_dsr_sim_no.append(postpaid_line_data_id.dsr_sim_no)
                                upg_dsr_imei_no.append(postpaid_line_data_id.dsr_imei_no)
                                upg_dsr_phone_no.append(postpaid_line_data_id.dsr_phone_no)
        else:
            for postpaid_line_data_id in upgrade_line_data:
                upg_dsr_sim_no.append(postpaid_line_data_id.dsr_sim_no)
                upg_dsr_imei_no.append(postpaid_line_data_id.dsr_imei_no)
                upg_dsr_phone_no.append(postpaid_line_data_id.dsr_phone_no)
        if 'dsr_offer_ids' in vals:
            offer_product_line = vals['dsr_offer_ids']
            if offer_product_line:
                for offer_product_line_id in offer_product_line:
                    offer_line_action = offer_product_line_id[0]
                    offer_line_id = offer_product_line_id[1]
                    offer_product_line_id = offer_product_line_id[2]
                    if offer_line_action != 2:    
                        if offer_product_line_id:
                            if 'dsr_imei_no' in offer_product_line_id:
                                offer_dsr_imei_no.append(offer_product_line_id['dsr_imei_no'])
                            else:
                                for offer_line_data_id in offer_line_data:
                                    if offer_line_data_id.id == offer_line_id:
                                        offer_dsr_imei_no.append(offer_line_data_id.dsr_imei_no)
                        else:
                            for offer_line_data_id in offer_line_data:
                                if offer_line_data_id.id == offer_line_id:
                                    offer_dsr_imei_no.append(offer_line_data_id.dsr_imei_no)
        else:
            for offer_line_data_id in offer_line_data:
                offer_dsr_imei_no.append(offer_line_data_id.dsr_imei_no)
        if pos_dsr_sim_no or pre_dsr_sim_no or upg_dsr_sim_no:
            for pos_dsr_sim_no_id in pos_dsr_sim_no:
                if pos_dsr_sim_no_id:
                    if pos_dsr_sim_no.count(pos_dsr_sim_no_id) > 1:
                        raise osv.except_osv(('Warning'),("Similar SIM number %s found in this particular transaction."%(pos_dsr_sim_no_id)))
                    if pos_dsr_sim_no_id in pre_dsr_sim_no or pos_dsr_sim_no_id in upg_dsr_sim_no:
                        raise osv.except_osv(('Warning'),("Similar SIM number %s found in this particular transaction."%(pos_dsr_sim_no_id)))
            for pre_dsr_sim_no_id in pre_dsr_sim_no:
                if pre_dsr_sim_no_id:
                    if pre_dsr_sim_no.count(pre_dsr_sim_no_id) > 1:
                        raise osv.except_osv(('Warning'),("Similar SIM number %s found in this particular transaction."%(pre_dsr_sim_no_id)))
                    if pre_dsr_sim_no_id in pos_dsr_sim_no or pre_dsr_sim_no_id in upg_dsr_sim_no:
                        raise osv.except_osv(('Warning'),("Similar SIM number %s found in this particular transaction."%(pre_dsr_sim_no_id)))
            for upg_dsr_sim_no_id in upg_dsr_sim_no:
                if upg_dsr_sim_no_id:
                    if upg_dsr_sim_no.count(upg_dsr_sim_no_id) > 1:
                        raise osv.except_osv(('Warning'),("Similar SIM number %s found in this particular transaction."%(upg_dsr_sim_no_id)))
                    if upg_dsr_sim_no_id in pos_dsr_sim_no or upg_dsr_sim_no_id in pre_dsr_sim_no:
                        raise osv.except_osv(('Warning'),("Similar SIM number %s found in this particular transaction."%(upg_dsr_sim_no_id)))
        if pos_dsr_imei_no or pre_dsr_imei_no or upg_dsr_imei_no or offer_dsr_imei_no:
            for pos_dsr_imei_no_id in pos_dsr_imei_no:
                if pos_dsr_imei_no_id:
                    if pos_dsr_imei_no.count(pos_dsr_imei_no_id) > 1:
                        raise osv.except_osv(('Warning'),("Similar IMEI number %s found in this particular transaction."%(pos_dsr_imei_no_id)))
                    if pos_dsr_imei_no_id in pre_dsr_imei_no or pos_dsr_imei_no_id in upg_dsr_imei_no:
                        raise osv.except_osv(('Warning'),("Similar IMEI number %s found in this particular transaction."%(pos_dsr_imei_no_id)))
            for pre_dsr_imei_no_id in pre_dsr_imei_no:
                if pre_dsr_imei_no_id:
                    if pre_dsr_imei_no.count(pre_dsr_imei_no_id) > 1:
                        raise osv.except_osv(('Warning'),("Similar IMEI number %s found in this particular transaction."%(pre_dsr_imei_no_id)))
                    if pre_dsr_imei_no_id in pos_dsr_imei_no or pre_dsr_imei_no_id in upg_dsr_imei_no:
                        raise osv.except_osv(('Warning'),("Similar IMEI number %s found in this particular transaction."%(pre_dsr_imei_no_id)))
            for upg_dsr_imei_no_id in upg_dsr_imei_no:
                if upg_dsr_imei_no_id:
                    if upg_dsr_imei_no.count(upg_dsr_imei_no_id) > 1:
                        raise osv.except_osv(('Warning'),("Similar IMEI number %s found in this particular transaction."%(upg_dsr_imei_no_id)))
                    if upg_dsr_imei_no_id in pos_dsr_imei_no or upg_dsr_imei_no_id in pre_dsr_imei_no:
                        raise osv.except_osv(('Warning'),("Similar IMEI number %s found in this particular transaction."%(upg_dsr_imei_no_id)))
            all_imei_no = pos_dsr_imei_no + pre_dsr_imei_no + upg_dsr_imei_no
            for offer_dsr_imei_no_id in offer_dsr_imei_no:
                if offer_dsr_imei_no_id:
                    if offer_dsr_imei_no_id not in all_imei_no:
                        raise osv.except_osv(('Warning!!'),("Marketing Offer IMEI %s not found in any other Transactions. Please use correct IMEI #"%(offer_dsr_imei_no_id)))
                    if offer_dsr_imei_no.count(offer_dsr_imei_no_id) > 1:
                        raise osv.except_osv(('Warning'),("Similar IMEI # %s found in Marketing Offers."%(offer_dsr_imei_no_id)))
        if pos_dsr_phone_no or pre_dsr_phone_no or upg_dsr_phone_no:
            for pos_dsr_phone_no_id in pos_dsr_phone_no:
                if pos_dsr_phone_no_id:
                    if pos_dsr_phone_no.count(pos_dsr_phone_no_id) > 1:
                        raise osv.except_osv(('Warning'),("Similar Phone number %s found in this particular transaction."%(pos_dsr_phone_no_id)))
                    if pos_dsr_phone_no_id in pre_dsr_phone_no or pos_dsr_phone_no_id in upg_dsr_phone_no:
                        raise osv.except_osv(('Warning'),("Similar Phone number %s found in this particular transaction."%(pos_dsr_phone_no_id)))
            for pre_dsr_phone_no_id in pre_dsr_phone_no:
                if pre_dsr_phone_no_id:
                    if pre_dsr_phone_no.count(pre_dsr_phone_no_id) > 1:
                        raise osv.except_osv(('Warning'),("Similar Phone number %s found in this particular transaction."%(pre_dsr_phone_no_id)))
                    if pre_dsr_phone_no_id in pos_dsr_phone_no or pre_dsr_phone_no_id in upg_dsr_phone_no:
                        raise osv.except_osv(('Warning'),("Similar Phone number %s found in this particular transaction."%(pre_dsr_phone_no_id)))
            for upg_dsr_phone_no_id in upg_dsr_phone_no:
                if upg_dsr_phone_no_id:
                    if upg_dsr_phone_no.count(upg_dsr_phone_no_id) > 1:
                        raise osv.except_osv(('Warning'),("Similar Phone number %s found in this particular transaction."%(upg_dsr_phone_no_id)))
                    if upg_dsr_phone_no_id in pos_dsr_phone_no or upg_dsr_phone_no_id in pre_dsr_phone_no:
                        raise osv.except_osv(('Warning'),("Similar Phone number %s found in this particular transaction."%(upg_dsr_phone_no_id)))
        return True

    def check_same_number(self, cr, uid, vals):
        pos_dsr_sim_no = []
        pos_dsr_imei_no = []
        pos_dsr_phone_no = []
        pre_dsr_sim_no = []
        pre_dsr_imei_no = []
        pre_dsr_phone_no = []
        upg_dsr_sim_no = []
        upg_dsr_imei_no = []
        upg_dsr_phone_no = []
        offer_dsr_imei_no = []
        prepaid_product_line = vals.get('prepaid_product_line', False)
        if 'postpaid_product_line' in vals:
            postpaid_product_line = vals['postpaid_product_line']
            for postpaid_product_line_id in postpaid_product_line:
                postpaid_product_line_id = postpaid_product_line_id[2]
                pos_dsr_sim_no.append(postpaid_product_line_id['dsr_sim_no'])
                pos_dsr_imei_no.append(postpaid_product_line_id['dsr_imei_no'])
                pos_dsr_phone_no.append(postpaid_product_line_id['dsr_phone_no'])
        if prepaid_product_line:
            prepaid_product_line = vals['prepaid_product_line']
            for postpaid_product_line_id in prepaid_product_line:
                postpaid_product_line_id = postpaid_product_line_id[2]
                pre_dsr_sim_no.append(postpaid_product_line_id['dsr_sim_no'])
                pre_dsr_imei_no.append(postpaid_product_line_id['dsr_imei_no'])
                pre_dsr_phone_no.append(postpaid_product_line_id['dsr_phone_no'])
        if 'upgrade_product_line' in vals:
            upgrade_product_line = vals['upgrade_product_line']
            for postpaid_product_line_id in upgrade_product_line:
                postpaid_product_line_id = postpaid_product_line_id[2]
                upg_dsr_sim_no.append(postpaid_product_line_id['dsr_sim_no'])
                upg_dsr_imei_no.append(postpaid_product_line_id['dsr_imei_no'])
                upg_dsr_phone_no.append(postpaid_product_line_id['dsr_phone_no'])
        if 'dsr_offer_ids' in vals:
            dsr_offer_ids = vals['dsr_offer_ids']
            if dsr_offer_ids:
                for dsr_offer_id in dsr_offer_ids:
                    offer_product_line_id = dsr_offer_id[2]
                    offer_dsr_imei_no.append(offer_product_line_id['dsr_imei_no'])
        if pos_dsr_sim_no or pre_dsr_sim_no or upg_dsr_sim_no:
            for pos_dsr_sim_no_id in pos_dsr_sim_no:
                if pos_dsr_sim_no_id:
                    if pos_dsr_sim_no.count(pos_dsr_sim_no_id) > 1:
                        raise osv.except_osv(('Warning'),("Similar SIM number %s found in this particular transaction."%(pos_dsr_sim_no_id)))
                    if pos_dsr_sim_no_id in pre_dsr_sim_no or pos_dsr_sim_no_id in upg_dsr_sim_no:
                        raise osv.except_osv(('Warning'),("Similar SIM number %s found in this particular transaction."%(pos_dsr_sim_no_id)))
            for pre_dsr_sim_no_id in pre_dsr_sim_no:
                if pre_dsr_sim_no_id:
                    if pre_dsr_sim_no.count(pre_dsr_sim_no_id) > 1:
                        raise osv.except_osv(('Warning'),("Similar SIM number %s found in this particular transaction."%(pre_dsr_sim_no_id)))
                    if pre_dsr_sim_no_id in pos_dsr_sim_no or pre_dsr_sim_no_id in upg_dsr_sim_no:
                        raise osv.except_osv(('Warning'),("Similar SIM number %s found in this particular transaction."%(pre_dsr_sim_no_id)))
            for upg_dsr_sim_no_id in upg_dsr_sim_no:
                if upg_dsr_sim_no_id:
                    if upg_dsr_sim_no.count(upg_dsr_sim_no_id) > 1:
                        raise osv.except_osv(('Warning'),("Similar SIM number %s found in this particular transaction."%(upg_dsr_sim_no_id)))
                    if upg_dsr_sim_no_id in pos_dsr_sim_no or upg_dsr_sim_no_id in pre_dsr_sim_no:
                        raise osv.except_osv(('Warning'),("Similar SIM number %s found in this particular transaction."%(upg_dsr_sim_no_id)))
        if pos_dsr_imei_no or pre_dsr_imei_no or upg_dsr_imei_no or offer_dsr_imei_no:
            for pos_dsr_imei_no_id in pos_dsr_imei_no:
                if pos_dsr_imei_no_id:
                    if pos_dsr_imei_no.count(pos_dsr_imei_no_id) > 1:
                        raise osv.except_osv(('Warning'),("Similar IMEI number %s found in this particular transaction."%(pos_dsr_imei_no_id)))
                    if pos_dsr_imei_no_id in pre_dsr_imei_no or pos_dsr_imei_no_id in upg_dsr_imei_no:
                        raise osv.except_osv(('Warning'),("Similar IMEI number %s found in this particular transaction."%(pos_dsr_imei_no_id)))
            for pre_dsr_imei_no_id in pre_dsr_imei_no:
                if pre_dsr_imei_no_id:
                    if pre_dsr_imei_no.count(pre_dsr_imei_no_id) > 1:
                        raise osv.except_osv(('Warning'),("Similar IMEI number %s found in this particular transaction."%(pre_dsr_imei_no_id)))
                    if pre_dsr_imei_no_id in pos_dsr_imei_no or pre_dsr_imei_no_id in upg_dsr_imei_no:
                        raise osv.except_osv(('Warning'),("Similar IMEI number %s found in this particular transaction."%(pre_dsr_imei_no_id)))
            for upg_dsr_imei_no_id in upg_dsr_imei_no:
                if upg_dsr_imei_no_id:
                    if upg_dsr_imei_no.count(upg_dsr_imei_no_id) > 1:
                        raise osv.except_osv(('Warning'),("Similar IMEI number %s found in this particular transaction."%(upg_dsr_imei_no_id)))
                    if upg_dsr_imei_no_id in pos_dsr_imei_no or upg_dsr_imei_no_id in pre_dsr_imei_no:
                        raise osv.except_osv(('Warning'),("Similar IMEI number %s found in this particular transaction."%(upg_dsr_imei_no_id)))
            all_imei_list = pos_dsr_imei_no + pre_dsr_imei_no + upg_dsr_imei_no
            for offer_dsr_imei_no_id in offer_dsr_imei_no:
                if offer_dsr_imei_no_id:
                    if offer_dsr_imei_no_id not in all_imei_list:
                        raise osv.except_osv(('Warning!!'),("Marketing Offer IMEI %s not found in any other Transactions. Please use correct IMEI #"%(offer_dsr_imei_no_id)))
                    if offer_dsr_imei_no.count(offer_dsr_imei_no_id) > 1:
                        raise osv.except_osv(('Warning'),("Similar IMEI # %s found in Marketing Offers."%(offer_dsr_imei_no_id)))
        if pos_dsr_phone_no or pre_dsr_phone_no or upg_dsr_phone_no:
            for pos_dsr_phone_no_id in pos_dsr_phone_no:
                if pos_dsr_phone_no_id:
                    if pos_dsr_phone_no.count(pos_dsr_phone_no_id) > 1:
                        raise osv.except_osv(('Warning'),("Similar Phone number %s found in this particular transaction."%(pos_dsr_phone_no_id)))
                    if pos_dsr_phone_no_id in pre_dsr_phone_no or pos_dsr_phone_no_id in upg_dsr_phone_no:
                        raise osv.except_osv(('Warning'),("Similar Phone number %s found in this particular transaction."%(pos_dsr_phone_no_id)))
            for pre_dsr_phone_no_id in pre_dsr_phone_no:
                if pre_dsr_phone_no_id:
                    if pre_dsr_phone_no.count(pre_dsr_phone_no_id) > 1:
                        raise osv.except_osv(('Warning'),("Similar Phone number %s found in this particular transaction."%(pre_dsr_phone_no_id)))
                    if pre_dsr_phone_no_id in pos_dsr_phone_no or pre_dsr_phone_no_id in upg_dsr_phone_no:
                        raise osv.except_osv(('Warning'),("Similar Phone number %s found in this particular transaction."%(pre_dsr_phone_no_id)))
            for upg_dsr_phone_no_id in upg_dsr_phone_no:
                if upg_dsr_phone_no_id:
                    if upg_dsr_phone_no.count(upg_dsr_phone_no_id) > 1:
                        raise osv.except_osv(('Warning'),("Similar Phone number %s found in this particular transaction."%(upg_dsr_phone_no_id)))
                    if upg_dsr_phone_no_id in pos_dsr_phone_no or upg_dsr_phone_no_id in pre_dsr_phone_no:
                        raise osv.except_osv(('Warning'),("Similar Phone number %s found in this particular transaction."%(upg_dsr_phone_no_id)))
        return True
    # def get_dealor_code(self,cr,uid,emp_id):
    #     #this function alter by shashank 27/11
        
    #     dealer_obj=self.pool.get('dealer.class')
    #     id=dealer_obj.search(cr,uid,[('dealer_id','=',emp_id)])
    #     res=dealer_obj.browse(cr,uid,id[0]).name
    #     return res

    def write_parent_data_to_child(self, cr, uid, ids):
        dsr_data = self.browse(cr, uid, ids)
        trans_date = dsr_data.dsr_date
        emp_id = dsr_data.dsr_sales_employee_id.id
        store_id = dsr_data.dsr_store_id.id
        market_id = dsr_data.dsr_market_id.id
        region_id = dsr_data.dsr_region_id.id
        dsr_transaction_id = dsr_data.dsr_transaction_id
        dsr_state = dsr_data.state 
        dsr_customer = dsr_data.dsr_cust_name
        emp_id = dsr_data.dsr_sales_employee_id.id
        dealer_code = dsr_data.dsr_dealer_code
        pseudo_date = dsr_data.pseudo_date
        dsr_designation_id = dsr_data.dsr_designation_id.id
        pre_obj = self.pool.get('wireless.dsr.prepaid.line')
        fea_obj = self.pool.get('wireless.dsr.feature.line')
        post_obj = self.pool.get('wireless.dsr.postpaid.line')
        postpaid_line_data = dsr_data.postpaid_product_line
        upgrade_line_data = dsr_data.upgrade_product_line
        accessory_line_data = dsr_data.acc_product_line
        prepaid_line_data = pre_obj.search(cr, uid, [('product_id','=',ids)])
        feature_line_data = fea_obj.search(cr, uid, [('feature_product_id','=',ids)])
        if postpaid_line_data:            
            for postpaid_line_id in postpaid_line_data:
                # postpaid_vals = post_obj.read(cr,uid,postpaid_line_id.id,['dsr_phone_no','dsr_temp_no'])                
                # if postpaid_vals['dsr_temp_no']==postpaid_vals['dsr_phone_no']:
                #     raise osv.except_osv(('Warning'), ("Phone Number & Temporary number cannot be same."))
                pos_id = postpaid_line_id.id
                self.pool.get('wireless.dsr.postpaid.line').write(cr, uid, [pos_id], {'dsr_act_date':trans_date,
                                                                                    'dsr_transaction_id':dsr_transaction_id,
                                                                                    'employee_id':emp_id,
                                                                                    'store_id':store_id,
                                                                                    'region_id':region_id,
                                                                                    'market_id':market_id,
                                                                                    'state':dsr_state,
                                                                                    'customer_name':dsr_customer,
                                                                                    'dealer_code':dealer_code,
                                                                                    'pseudo_date':pseudo_date,
                                                                                    'dsr_designation_id':dsr_designation_id
                                                                                    })
        if prepaid_line_data:
            for prepaid_line_id in prepaid_line_data:
                self.pool.get('wireless.dsr.prepaid.line').write(cr, uid, [prepaid_line_id], {'dsr_act_date':trans_date,
                                                                                            'dsr_transaction_id':dsr_transaction_id,
                                                                                            'employee_id':emp_id,
                                                                                            'store_id':store_id,
                                                                                            'region_id':region_id,
                                                                                            'market_id':market_id,
                                                                                            'state':dsr_state,
                                                                                            'customer_name':dsr_customer,
                                                                                            'dealer_code':dealer_code,
                                                                                            'pseudo_date':pseudo_date,
                                                                                            'dsr_designation_id':dsr_designation_id
                                                                                         })   
        if feature_line_data:
            for feature_line_id in feature_line_data:
                self.pool.get('wireless.dsr.feature.line').write(cr, uid, [feature_line_id], {'dsr_act_date':trans_date,
                                                                                            'dsr_transaction_id':dsr_transaction_id,
                                                                                            'employee_id':emp_id,
                                                                                            'store_id':store_id,
                                                                                            'region_id':region_id,
                                                                                            'market_id':market_id,
                                                                                            'state':dsr_state,
                                                                                            'customer_name':dsr_customer,
                                                                                            'dealer_code':dealer_code,
                                                                                            'pseudo_date':pseudo_date,
                                                                                            'dsr_designation_id':dsr_designation_id
                                                                                            })
        if upgrade_line_data:
            for upgrade_line_id in upgrade_line_data:
                upgrade_id = upgrade_line_id.id
                self.pool.get('wireless.dsr.upgrade.line').write(cr, uid, [upgrade_id], {'dsr_act_date':trans_date,
                                                                                        'dsr_transaction_id':dsr_transaction_id,
                                                                                        'employee_id':emp_id,
                                                                                        'store_id':store_id,
                                                                                        'region_id':region_id,
                                                                                        'market_id':market_id,
                                                                                        'state':dsr_state,
                                                                                        'customer_name':dsr_customer,
                                                                                        'dealer_code':dealer_code,
                                                                                        'pseudo_date':pseudo_date,
                                                                                        'dsr_designation_id':dsr_designation_id
                                                                                        })
        if accessory_line_data:
            for acc_line_id in accessory_line_data:
                acc_id = acc_line_id.id
                self.pool.get('wireless.dsr.acc.line').write(cr, uid, [acc_id], {'dsr_act_date':trans_date,
                                                                                'dsr_transaction_id':dsr_transaction_id,
                                                                                'employee_id':emp_id,
                                                                                'store_id':store_id,
                                                                                'region_id':region_id,
                                                                                'market_id':market_id,
                                                                                'state':dsr_state,
                                                                                'customer_name':dsr_customer,
                                                                                'dealer_code':dealer_code,
                                                                                'pseudo_date':pseudo_date,
                                                                                'dsr_designation_id':dsr_designation_id
                                                                                })
        return True

    def check_lock_down(self, cr, uid, vals, transaction_date, postpaid_ids, upgrade_ids, dsr_pseudo_date):
        # dsr_data = self.browse(cr, uid, ids[0])        
        package_comm = self.pool.get('packaged.commission.tracker')
########## Code changes done for ship to change, allow editable those records even lock down period which are in pending state
        ship_to = False
        status = False
        if postpaid_ids or upgrade_ids:
            if not ship_to and not status:
                for postpaid_data in postpaid_ids:
                    ship_to = postpaid_data.dsr_ship_to
                    status = postpaid_data.state
                    break
            if not ship_to or not status:
                for upgrade_data in upgrade_ids:
                    ship_to = upgrade_data.dsr_ship_to
                    status = upgrade_data.state
                    break

        pseudo_date = False
        dsr_date = transaction_date
        dsr_date_strp = datetime.datetime.strptime(dsr_date, '%Y-%m-%d').date()
        dsr_date_month = dsr_date_strp.month
        dsr_date_year = dsr_date_strp.year
        start_date = str('%s-%s-01' % (int(dsr_date_year),int(dsr_date_month)))
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        start_date = start_date.date().strftime('%Y-%m-%d')
        days_month = calendar.monthrange(dsr_date_year,dsr_date_month)[1]
        end_date = str('%s-%s-%s' % (int(dsr_date_year),int(dsr_date_month),int(days_month)))
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        end_date = end_date.date().strftime('%Y-%m-%d')
        package_ids = package_comm.search(cr, uid, [('start_date','=',start_date),('end_date','=',end_date),('pre_package_comm','=',False)], limit=1)
        if package_ids:
            pseudo_date = (datetime.datetime.strptime(dsr_date, '%Y-%m-%d') + relativedelta(days=30))
            pseudo_date = pseudo_date.date().strftime('%Y-%m-%d')
############### code changes done in April 2015 change for commission team ###########
        user_list = []
        cr.execute("select id from res_groups where name like 'Commission Analyst' ")
        group_ids = cr.fetchall()
        group_ids = group_ids[0][0]
        
        cr.execute("select uid from res_groups_users_rel where gid=%s",(group_ids,))
        user_ids_list = cr.fetchall()
        for user_id in user_ids_list:
            user_list.append(user_id[0])        

        ############ Lock Down Date #####################
        lock_down_search = []

    #######  groups from lock down master #############
        cr.execute("select lid from group_lock_rel_master")
        group_ids = map(lambda x: x[0], cr.fetchall())

    #######  fetch groups assigned to uid  ############
        cr.execute("select gid from res_groups_users_rel where uid=%s"%(uid,))
        group_user_ids = map(lambda x: x[0], cr.fetchall())

    #######  match group_user_ids in group_ids  #############
        for group_user_id in group_user_ids:
            if group_user_id in group_ids:
                cr.execute("select gid from group_lock_rel_master where lid=%s"%(group_user_id))
                lock_down_search = map(lambda x: x[0], cr.fetchall())

        if lock_down_search:
            lock_down_data = self.pool.get('lock.down.master').browse(cr, uid, lock_down_search[0])
            unlock_start_date = lock_down_data.unlock_start_date
            unlock_end_date = lock_down_data.unlock_end_date
            lock_down_date = lock_down_data.date

            # transaction_date = dsr_data.dsr_date
            dsr_trans_date = datetime.datetime.strptime(transaction_date, '%Y-%m-%d')
            trans_date = dsr_trans_date.strftime('%d')
            trans_mon = dsr_trans_date.strftime('%Y-%m')
            max_date = (dsr_trans_date + relativedelta(months=1))
            max_mon = max_date.strftime('%Y-%m')
            ################ Current Date #################
            current_date = time.strftime('%Y-%m-%d')
            ds = datetime.datetime.strptime(current_date, '%Y-%m-%d')
            current_mon = ds.strftime('%Y-%m')
            current_date = ds.strftime('%d')

            if trans_mon == current_mon:
                vals.update({'pseudo_date':False})
                return vals
            elif max_mon == current_mon:
                if int(current_date) > int(lock_down_date):
                    if ship_to and (status in ('pending','done')) and (not dsr_pseudo_date):
                        if uid in user_list:
                            if (transaction_date >= unlock_start_date) and (transaction_date <= unlock_end_date) and status == 'done':
                                vals.update({'pseudo_date':pseudo_date})
                                return vals
                            else:
                                vals.update({'pseudo_date':False})
                                return vals
                        else:
                            if (transaction_date >= unlock_start_date) and (transaction_date <= unlock_end_date) and (status == 'done'):
                                vals.update({'pseudo_date':pseudo_date})
                                return vals
                            elif (transaction_date >= unlock_start_date) and (transaction_date <= unlock_end_date):
                                vals.update({'pseudo_date':False})
                                return vals
                            else:
                                raise osv.except_osv(_('Warning'),_("Ship-to Transactions update is locked down for this transaction date."))
                    else:
                        if uid in user_list:
                            vals.update({'pseudo_date':False})
                            return vals
                        else:
                            raise osv.except_osv(_('Warning'),_("DSR Entry is locked down for this transaction date."))
                else:
                    vals.update({'pseudo_date':False})
                    return vals
            else:
                if ship_to and (status in ('pending','done')) and (not dsr_pseudo_date):
                    if uid in user_list:
                        if (transaction_date >= unlock_start_date) and (transaction_date <= unlock_end_date) and (status == 'done'):
                            vals.update({'pseudo_date':pseudo_date})
                            return vals
                        else:
                            vals.update({'pseudo_date':False})
                            return vals
                    else:
                        if (transaction_date >= unlock_start_date) and (transaction_date <= unlock_end_date) and (status == 'done'):
                            vals.update({'pseudo_date':pseudo_date})
                            return vals
                        elif (transaction_date >= unlock_start_date) and (transaction_date <= unlock_end_date):
                            vals.update({'pseudo_date':False})
                            return vals
                        else:
                            raise osv.except_osv(_('Warning'),_("Ship-to Transactions update is locked down for this transaction date."))
                else:
                    if uid in user_list:
                        vals.update({'pseudo_date':False})
                        return vals
                    else:
                        raise osv.except_osv(_('Warning'),_("DSR Entry is locked down for this transaction date."))
        return vals

    def _update_rate_plan_write(self, cr, uid, pos_new_values, postpaid_ids, pos_obj):
        prod_obj = self.pool.get('product.product')
        line_obj = self.pool.get('transaction.line.soc.rel')
        pos_dict = {}
        id_list = []
        count_len = 0
        cr.execute("select distinct(soc_code) from transaction_line_soc_rel")
        main_soc_code = map(lambda x: x[0], cr.fetchall())
        
        for pos_new_values_each in pos_new_values:
            if pos_new_values_each[1]:
                if pos_new_values_each[0] != 2:
                    pos_data = pos_obj.browse(cr, uid, pos_new_values_each[1])
                    if pos_new_values_each[2]:
                        soc_code = pos_new_values_each[2].get('dsr_product_code')
                        ban_no = pos_new_values_each[2].get('dsr_cust_ban_no')
                        if not soc_code:
                            soc_code = pos_data.dsr_product_code.id
                        if not ban_no:
                            ban_no = pos_data.dsr_cust_ban_no
                    else:
                        soc_code = pos_data.dsr_product_code.id
                        ban_no = pos_data.dsr_cust_ban_no
                else:
                    soc_code = False
                    ban_no = False
            else:
                soc_code = pos_new_values_each[2].get('dsr_product_code')
                ban_no = pos_new_values_each[2].get('dsr_cust_ban_no')
            if soc_code and ban_no:
                if not pos_dict.get(ban_no):
                    pos_dict['%s'%(ban_no)] = []
                pos_dict[ban_no].append(soc_code)
                id_list.append(pos_new_values_each[1])
        for d in pos_dict:
            for pos_soc_code_each in pos_dict[d]:
                if pos_soc_code_each in main_soc_code:
                    prod_data = prod_obj.browse(cr, uid, pos_soc_code_each)
                    required_line_list = line_obj.search(cr, uid, [('sub_soc_code','=',False),('soc_code','=',pos_soc_code_each)])
                    cr.execute("select distinct(sub_soc_code) from transaction_line_soc_rel where soc_code = %s"%(pos_soc_code_each))
                    sub_soc_code = map(lambda x: x[0], cr.fetchall())
                    count = len(required_line_list)
                    if len(required_line_list) >= pos_dict[d].count(pos_soc_code_each):
                        for pos_new_values_each in pos_new_values:
                            cr.execute("select id from credit_line_limit where sequence = %s"%(count))
                            line_no = map(lambda x: x[0], cr.fetchall())
                            if pos_new_values_each[1]:
                                if pos_new_values_each[0] != 2:
                                    pos_data = pos_obj.browse(cr, uid, pos_new_values_each[1])
                                    if pos_new_values_each[2]:
                                        soc_code = pos_new_values_each[2].get('dsr_product_code')
                                        ban_no = pos_new_values_each[2].get('dsr_cust_ban_no')
                                        if not soc_code:
                                            soc_code = pos_data.dsr_product_code.id
                                        if not ban_no:
                                            ban_no = pos_data.dsr_cust_ban_no
                                    else:
                                        soc_code = pos_data.dsr_product_code.id
                                        ban_no = pos_data.dsr_cust_ban_no
                                else:
                                    soc_code = False
                                    ban_no = False
                            else:
                                soc_code = pos_new_values_each[2].get('dsr_product_code')
                                ban_no = pos_new_values_each[2].get('dsr_cust_ban_no')
                            
                            if soc_code and ban_no:
                                if pos_soc_code_each == soc_code and d == ban_no:
                                    if pos_new_values_each[2]:
                                        pos_new_values_each[2].update({'dsr_line_no':line_no[0]})
                                    else:
                                        pos_new_values_each[2] = {'dsr_line_no':line_no[0]}
                                        pos_new_values_each[0] = 1
                                    count -= 1
                                elif pos_new_values_each[2] and d == ban_no:
                                    pos_new_values_each[2].update({'dsr_line_no':False})
                    else:
                        raise osv.except_osv(('Warning!!'),('You have entered more than %s lines with SOC Code %s and same BAN # %s'%(len(required_line_list),prod_data.default_code,d)))
       ############### Validation based on Search in whole system with same BAN and SOC Code #########
                    pos_same_ban_soc_ids = pos_obj.search(cr, uid, [('dsr_product_code','=',pos_soc_code_each),('dsr_cust_ban_no','=',d),('id','not in',id_list),('state','=','done')])
                    if len(required_line_list) < (pos_dict[d].count(pos_soc_code_each) + len(pos_same_ban_soc_ids)):
                        raise osv.except_osv(('Warning!!'),('System already has %s lines with SOC Code %s and same BAN # %s'%(len(required_line_list),prod_data.default_code,d)))                    
                    non_required_line_list = line_obj.search(cr, uid, [('sub_soc_code','!=',False),('soc_code','=',pos_soc_code_each)])
                    if non_required_line_list:
                        pos_soc_code_sub = [x for x in pos_dict[d] if x != pos_soc_code_each]
                        if len(non_required_line_list) < len(pos_soc_code_sub):
                            raise osv.except_osv(('Warning!!'),('You have reached maximum line limits for this plan %s with same BAN # %s. Please try after removing additional Line.'%(prod_data.default_code,d)))
                        count = len(required_line_list)
                        for pos_soc_code_sub_each in pos_soc_code_sub:
                            if pos_soc_code_sub_each not in sub_soc_code:
                                prod_data_sub = prod_obj.browse(cr, uid, pos_soc_code_sub_each)
                                raise osv.except_osv(('Warning!!'),('You can not add %s Rate Plan with %s Rate Plan'%(prod_data_sub.default_code,prod_data.default_code)))
                            else:
                                cr.execute("select line_no from transaction_line_soc_rel where soc_code = %s and sub_soc_code = %s"%(pos_soc_code_each,pos_soc_code_sub_each))
                                line_no = map(lambda x: x[0], cr.fetchall())
                                for pos_new_values_each in pos_new_values:
                                    if pos_new_values_each[1]:
                                        if pos_new_values_each[0] != 2:
                                            pos_data = pos_obj.browse(cr, uid, pos_new_values_each[1])
                                            if pos_new_values_each[2]:
                                                soc_code = pos_new_values_each[2].get('dsr_product_code')
                                                ban_no = pos_new_values_each[2].get('dsr_cust_ban_no')
                                                if not soc_code:
                                                    soc_code = pos_data.dsr_product_code.id
                                                if not ban_no:
                                                    ban_no = pos_data.dsr_cust_ban_no
                                            else:
                                                soc_code = pos_data.dsr_product_code.id
                                                ban_no = pos_data.dsr_cust_ban_no
                                        else:
                                            soc_code = False
                                            ban_no = False
                                    else:
                                        soc_code = pos_new_values_each[2].get('dsr_product_code')
                                        ban_no = pos_new_values_each[2].get('dsr_cust_ban_no')
                                
                                    if soc_code and ban_no:
                                        if pos_soc_code_sub_each == soc_code and d == ban_no:
                                            if pos_new_values_each[2]:
                                                pos_new_values_each[2].update({'dsr_line_no':line_no[0]})
                                            else:
                                                pos_new_values_each[2] = {'dsr_line_no':line_no[0]}
                                                pos_new_values_each[0] = 1
                                            count += 1
                                        elif pos_new_values_each[2] and (not pos_new_values_each[2].get('dsr_line_no')):
                                            pos_new_values_each[2].update({'dsr_line_no':False})
                    break
                else:
                    for pos_new_values_each in pos_new_values:
                        pos_data = pos_obj.browse(cr, uid, pos_new_values_each[1])
                        ban_no = False
                        soc_code = False
                        if pos_new_values_each[2]:
                            ban_no = pos_new_values_each[2].get('dsr_cust_ban_no')
                            soc_code = pos_new_values_each[2].get('dsr_product_code')
                        if not ban_no:
                            ban_no = pos_data.dsr_cust_ban_no
                        if not soc_code:
                            soc_code = pos_data.dsr_product_code.id
                        if (ban_no == d) and (soc_code == pos_soc_code_each) and (pos_new_values_each[2]) and (not pos_new_values_each[2].get('dsr_line_no')):
                            pos_new_values_each[2].update({'dsr_line_no':False})
        return pos_new_values

    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int,long)):
            ids = [ids]
        self_data = self.browse(cr, uid, ids[0])
        pos_obj = self.pool.get('wireless.dsr.postpaid.line')
        upg_obj = self.pool.get('wireless.dsr.upgrade.line')
        offer_obj = self.pool.get('dsr.marketing.offers')
        if 'dsr_cust_email_id' in vals:
            email = vals['dsr_cust_email_id']
            email_match(email)
        if 'dsr_date' in vals:
            transaction_date = vals['dsr_date']
        else:
            transaction_date = self_data.dsr_date
        if 'state' in vals:
            if vals['state'] == 'done':
                self.validation_check(cr, uid, ids)
                self.validation_check_eip_warranty(cr, uid, ids)
        if 'dsr_transaction_id' in vals:
            reg=re.compile('^[a-z0-9\.]+$')
            re_res=reg.match(vals['dsr_transaction_id'])
            if not re_res:
                raise osv.except_osv(('Error!!!'),('Special characters in "Transaction Id" not allowed.'))
        if 'dsr_store_id' in vals:
            dsr_store_id = vals['dsr_store_id']
        else:
            dsr_store_id = self_data.dsr_store_id.id
        if 'dsr_sales_employee_id' in vals:
            emp_id = vals['dsr_sales_employee_id']
        else:
            emp_id = self_data.dsr_sales_employee_id.id
        if 'is_offer' in vals:
            if not vals['is_offer']:
                offer_ids = offer_obj.search(cr, uid, [('dsr_id','=',ids[0])])
                offer_obj.unlink(cr, uid, offer_ids)
                vals.update({'gross_disc':0.00})
        postpaid_ids = self_data.postpaid_product_line
        upgrade_ids = self_data.upgrade_product_line
        pseudo_date = self_data.pseudo_date
        self.check_same_number_write(cr, uid, ids, vals)
        if vals.get('postpaid_product_line'):
            vals['postpaid_product_line'] = self._update_rate_plan_write(cr, uid, vals.get('postpaid_product_line'), postpaid_ids, pos_obj)
        if vals.get('upgrade_product_line'):
            vals['upgrade_product_line'] = self._update_rate_plan_write(cr, uid, vals.get('upgrade_product_line'), postpaid_ids, upg_obj)
        # if vals.get('dsr_offer_ids') or vals.get('postpaid_product_line') or vals.get('prepaid_product_line') or vals.get('upgrade_product_line') or vals.get('feature_product_line'):
        #     self.check_offer_coupon_code(cr, uid, self_data, vals)
        vals = self.check_lock_down(cr, uid, vals, transaction_date, postpaid_ids, upgrade_ids, pseudo_date)
        res = super(wireless_dsr, self).write(cr, uid, ids, vals, context=context)
        self.write_parent_data_to_child(cr, uid, ids[0])
            
    ########### Parent Gross Revenue Field Update because it ran before child functional field calculations ##########
        gross_vals = self._compute_all(cr, uid, [ids[0]], False, False, context=context)
        cr.execute("update wireless_dsr set gross_rev = %s, gross_comm_per_line = %s where id = %s"%(gross_vals[ids[0]]['gross_rev'],gross_vals[ids[0]]['gross_comm_per_line'],ids[0]))

        return res

    def _update_rate_plan(self, cr, uid, postpaid_ids, pos_obj):
        prod_obj = self.pool.get('product.product')
        line_obj = self.pool.get('transaction.line.soc.rel')
        pos_dict = {}
        cr.execute("select distinct(soc_code) from transaction_line_soc_rel")
        main_soc_code = map(lambda x: x[0], cr.fetchall())
        for pos_data in postpaid_ids:
            soc_code = pos_data[2].get('dsr_product_code')
            ban_no = pos_data[2].get('dsr_cust_ban_no')
            if not pos_dict.get(ban_no):
                pos_dict['%s'%(ban_no)] = []
            pos_dict[ban_no].append(soc_code)

        for d in pos_dict:
            for pos_soc_code_each in pos_dict[d]:
                if pos_soc_code_each in main_soc_code:
                    prod_data = prod_obj.browse(cr, uid, pos_soc_code_each)
                    required_line_list = line_obj.search(cr, uid, [('sub_soc_code','=',False),('soc_code','=',pos_soc_code_each)])
                    cr.execute("select distinct(sub_soc_code) from transaction_line_soc_rel where soc_code = %s"%(pos_soc_code_each))
                    sub_soc_code = map(lambda x: x[0], cr.fetchall())
                    count = len(required_line_list)
                    if len(required_line_list) >= pos_dict[d].count(pos_soc_code_each):                    
                        for pos_data in postpaid_ids:
                            if (d == pos_data[2].get('dsr_cust_ban_no')) and (pos_soc_code_each == pos_data[2].get('dsr_product_code')):
                                cr.execute("select id from credit_line_limit where sequence = %s"%(count))
                                line_no = map(lambda x: x[0], cr.fetchall())
                                pos_data[2].update({'dsr_line_no':line_no[0]})
                                count -= 1
                    else:
                        raise osv.except_osv(('Warning!!'),('You have entered more than %s lines with SOC Code %s and same BAN # %s'%(len(required_line_list),prod_data.default_code,d)))
       ############### Validation based on Search in whole system with same BAN and SOC Code #########
                    pos_same_ban_soc_ids = pos_obj.search(cr, uid, [('dsr_product_code','=',pos_soc_code_each),('dsr_cust_ban_no','=',d),('state','=','done')])
                    if len(required_line_list) < (pos_dict[d].count(pos_soc_code_each) + len(pos_same_ban_soc_ids)):
                        raise osv.except_osv(('Warning!!'),('System already has %s lines with SOC Code %s and same BAN # %s'%(len(required_line_list),prod_data.default_code,d)))
      ############### Subordinate SOC Code ####################             
                    non_required_line_list = line_obj.search(cr, uid, [('sub_soc_code','!=',False),('soc_code','=',pos_soc_code_each)])
                    if non_required_line_list:
                        pos_soc_code_sub = [x for x in pos_dict[d] if x != pos_soc_code_each]
                        if len(non_required_line_list) < len(pos_soc_code_sub):
                            raise osv.except_osv(('Warning!!'),('You have reached maximum line limits for this plan %s with same BAN # %s. Please try after removing additional Line.'%(prod_data.default_code,d)))
                        count = len(required_line_list)
                        for pos_soc_code_sub_each in pos_soc_code_sub:                    
                            if pos_soc_code_sub_each not in sub_soc_code:
                                prod_data_sub = prod_obj.browse(cr, uid, pos_soc_code_sub_each)
                                raise osv.except_osv(('Warning!!'),('You can not add %s Rate Plan with %s Rate Plan'%(prod_data_sub.default_code,prod_data.default_code)))
                            #### need to verify
                            else:
                                cr.execute("select line_no from transaction_line_soc_rel where soc_code = %s and sub_soc_code = %s"%(pos_soc_code_each,pos_soc_code_sub_each))
                                line_no = map(lambda x: x[0], cr.fetchall())
                                for pos_data in postpaid_ids:
                                    if (d == pos_data[2].get('dsr_cust_ban_no')) and (pos_soc_code_sub_each == pos_data[2].get('dsr_product_code')):
                                        pos_data[2].update({'dsr_line_no':line_no[0]})
                                        count += 1
                    break
        return postpaid_ids

    def create(self, cr, uid, vals, context=None):
        pos_obj=self.pool.get('wireless.dsr.postpaid.line')
        upg_obj=self.pool.get('wireless.dsr.upgrade.line')
        if vals['dsr_cust_email_id']:
            email = vals['dsr_cust_email_id']
            email_match(email)
        if vals['dsr_transaction_id']:
            reg = re.compile('^[a-z0-9\.]+$')
            re_res = reg.match(vals['dsr_transaction_id'])
            if not re_res:
                raise osv.except_osv(('Error!!!'),('Special characters in "Transaction Id" not allowed.'))
        transaction_date = vals['dsr_date']
        if not vals['is_offer']:
            vals['dsr_offer_ids'] = False
        vals = self.check_lock_down(cr, uid, vals, transaction_date, False, False, False)
        self.check_same_number(cr, uid, vals)
        # if vals['dsr_offer_ids']:
        #     self.check_offer_coupon_code(cr, uid, False, vals)
        if vals.get('name','WV')=='WV':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'wireless.dsr') or 'WV'
        postpaid_ids = vals.get('postpaid_product_line')
        if postpaid_ids:
            postpaid_data = self._update_rate_plan(cr, uid, postpaid_ids, pos_obj)
            vals['postpaid_product_line'] = postpaid_data
        upgrade_ids = vals.get('upgrade_product_line')
        if upgrade_ids:
            upgrade_data = self._update_rate_plan(cr, uid, upgrade_ids, upg_obj)
            vals['upgrade_product_line'] = upgrade_data
        res = super(wireless_dsr, self).create(cr, uid, vals, context=context)
        self.write_parent_data_to_child(cr, uid, res)
                    
    ########### Parent Gross Revenue Field Update because it ran before child functional field calculations ##########
        gross_vals = self._compute_all(cr, uid, [res], False, False, context=context)
        cr.execute("update wireless_dsr set gross_rev = %s, gross_comm_per_line = %s where id = %s"%(gross_vals[res]['gross_rev'],gross_vals[res]['gross_comm_per_line'],res))

        return res

    def copy(self, cr, uid, id, default=None, context=None):
        if uid != 1:
            raise osv.except_osv(('Warning!!'),('You are not allowed to duplicate records.'))
        res = super(wireless_dsr, self).copy(cr, uid, id, default, context)
        return res

wireless_dsr()

class dsr_marketing_offers(osv.osv):
    _name = 'dsr.marketing.offers'
    
    _columns = {
                'dsr_disc_type':fields.many2one('discount.type.master','Offer Type', required=True),
                'dsr_discount':fields.float('Discount $'),
                'dsr_coupon_code':fields.many2one('offer.coupon.code','Coupon Code', required=True),
                'dsr_imei_no':fields.char('IMEI #'),
                'dsr_id':fields.many2one('wireless.dsr','DSR Id')
    }

    def onchange_coupon(self, cr, uid, ids, coupon_code):
        coupon_obj = self.pool.get('offer.coupon.code')
        dsr_disc_type = []
        if coupon_code:
            coupon_data = coupon_obj.browse(cr, uid, coupon_code)
            discount = coupon_data.amount
            disc_type_data = coupon_data.dsr_disc_type
            for disc_type_each in disc_type_data:
                dsr_disc_type.append(disc_type_each.id)
            if len(dsr_disc_type) > 1:
                domain = {'dsr_disc_type':[('id','in',dsr_disc_type)]}
                dsr_disc_type = False
            elif len(dsr_disc_type) == 1:
                domain = {'dsr_disc_type':[('id','in',dsr_disc_type)]}
                dsr_disc_type = dsr_disc_type[0]
            else:
                domain = {'dsr_disc_type':[]}
                dsr_disc_type = False
            return {'value':{'dsr_discount':discount,'dsr_disc_type':dsr_disc_type},'domain':domain}
        domain = {'dsr_disc_type':[]}
        return {'value':{'dsr_discount':0,'dsr_disc_type':False},'domain':domain}

    def onchange_imei(self, cr, uid, ids, imei):
        if imei:
            imei_check(imei)
        return {}

    def create(self, cr, uid, vals, context=None):
        offer_obj = self.pool.get('offer.coupon.code')
        imei = vals['dsr_imei_no']
        imei_short = False
        if imei:
            imei_check(imei)
            imei_short = imei[:8]
        dsr_coupon_code = vals['dsr_coupon_code']
        offer_data = offer_obj.browse(cr, uid, dsr_coupon_code)
        tac_ids = offer_data.include_tac_ids
        if tac_ids:
            for tac_data in tac_ids:
                if tac_data.tac_code != imei_short:
                    raise osv.except_osv(('Error!!'),('Coupon Code %s is not applicable on entered IMEI %s.'%(offer_data.coupon_code,imei)))
        qty_limit = offer_data.qty_limit
        if qty_limit > 0:
            self_ids = self.search(cr, uid, [('dsr_coupon_code','=',dsr_coupon_code)])
            if qty_limit < len(self_ids):
                raise osv.except_osv(('Warning!!'),('Coupon Code %s has exceeded customer limit.'%(offer_data.coupon_code)))
        res = super(dsr_marketing_offers, self).create(cr, uid, vals, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        offer_obj = self.pool.get('offer.coupon.code')
        for id in ids:
            self_data = self.browse(cr, uid, id)
            imei = vals.get('dsr_imei_no')
            imei_short = False
            if imei:
                imei_check(imei)
                imei_short = imei[:8]
            dsr_coupon_code = vals.get('dsr_coupon_code')
            if not dsr_coupon_code:
                dsr_coupon_code = self_data.dsr_coupon_code.id
            offer_data = offer_obj.browse(cr, uid, dsr_coupon_code)
            tac_ids = offer_data.include_tac_ids
            if tac_ids:
                for tac_data in tac_ids:
                    if tac_data.tac_code != imei_short:
                        raise osv.except_osv(('Error!!'),('Coupon Code %s is not applicable on entered IMEI %s.'%(offer_data.coupon_code,imei)))
            qty_limit = offer_data.qty_limit
            if qty_limit > 0:
                self_ids = self.search(cr, uid, [('dsr_coupon_code','=',dsr_coupon_code)])
                if qty_limit < len(self_ids):
                    raise osv.except_osv(('Warning!!'),('Coupon Code %s has exceeded customer limit.'%(offer_data.coupon_code)))
        res = super(dsr_marketing_offers, self).write(cr, uid, ids, vals, context=context)
        return res

dsr_marketing_offers()

############# Accessory Line One2many #######################
class wireless_dsr_acc_line(osv.osv):
    _name = 'wireless.dsr.acc.line'
    _description = "Wireless DSR Accessory Line"
    _order = 'id desc'

    def _calculate_revenue(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        line = self.browse(cr, uid, ids[0], context=context)
        dsr_id = line.product_id.id
        dsr_data = self.pool.get('wireless.dsr').browse(cr, uid, dsr_id)
        trans_date = dsr_data.dsr_date
        emp_des = dsr_data.dsr_designation_id.id
        non_comm = line.dsr_sku_select.non_comm
        comm_percent = 0.00
        base_comm_obj = self.pool.get('comm.basic.commission.formula')
        base_comm_search = base_comm_obj.search(cr, uid, [('comm_designation','=',emp_des),('comm_start_date','<=',trans_date),('comm_end_date','>=',trans_date),('comm_inactive','=',False)])
        if base_comm_search:
            comm_percent = base_comm_obj.browse(cr, uid, base_comm_search[0]).comm_percent
        else:
            base_comm_search = base_comm_obj.search(cr, uid, [('comm_start_date','<=',trans_date),('comm_end_date','>=',trans_date),('comm_inactive','=',False)])
            if base_comm_search:
                comm_percent = base_comm_obj.browse(cr, uid, base_comm_search[0]).comm_percent
        res[line.id] = {
                'dsr_rev_gen': 0.00,
                'dsr_acc_mrc':0.00,
                'dsr_comm_per_line':0.00
            }
        val = val1 = val2 = add = tot = disc = val3 = comm = 0.00
        val = line.dsr_list_price
        val1 = line.dsr_quantity
        add = val * val1
        val2 = line.dsr_disc_percent.disc_percent
        comm = line.dsr_acc_comm
        val3 = comm * val1
        if val2:
            disc = (add * val2)/100
        tot = add - disc
        
        ### code to also have 35 % of the Total amt as WV Commission generated accessory commission amount is zero.
        ### or else continue with the current formula
        if comm  <= 0.0 and (not non_comm):
            rev = 0.35 * tot
        elif non_comm:
            rev = 0.00
            tot = 0.00
        else:
            rev = val3 - add + tot
        ###### code ends here
        
        res[line.id]['dsr_rev_gen'] = rev
        res[line.id]['dsr_acc_mrc'] = tot
        res[line.id]['dsr_comm_per_line'] = (rev * comm_percent) / 100
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('wireless.dsr.acc.line').browse(cr, uid, ids, context=context):
            result[line.id] = True
        return result.keys()

    _columns = {
                'product_id':fields.many2one('wireless.dsr','Product Id'),
                'dsr_trans_type':fields.selection(_prod_type, 'Transaction Type'),
                'dsr_phone_no':fields.char('Mobile #', size=10),
                'dsr_disc_percent':fields.many2one('discount.master', 'Discount(%)'),
                'dsr_list_price':fields.float('MRP'),
                'dsr_quantity':fields.integer('QTY'),
                'dsr_sku_select':fields.many2one('wireless.acc.sku.master','SKU Code'),
                'dsr_acc_comm':fields.float('Commission'),
                'dsr_rev_gen':fields.function(_calculate_revenue, string="Revenue Generated", type='float', multi='sums',
                        store={
                                'wireless.dsr.acc.line': (_get_order, [], 10),
                }),
                'dsr_acc_mrc':fields.function(_calculate_revenue, string="Total Rev Gen.", type='float', multi='sums',
                        store={
                                'wireless.dsr.acc.line': (_get_order, [], 10),
                }),
                'dsr_comm_per_line':fields.function(_calculate_revenue, string="Commission Per line", type='float', multi='sums',
                        store={
                                'wireless.dsr.acc.line': (_get_order, [], 10),
                }),
                'dsr_emp_type':fields.many2one('dsr.employee.type','T-Mobile Employee'),
                'is_emp_upg':fields.boolean('Employee Upgrade'),
                'dsr_p_number':fields.char('P-number'),
                'dsr_product_sku':fields.char('SKU Code', size=1024),
                'dsr_act_date':fields.date('Activation Date'),
                'pseudo_date':fields.date('Pseudo Transaction Date'),
                'dsr_deact_date':fields.date('DeActivation Date'),
                'act_recon':fields.boolean('Act Reconciled'),
                'deact_recon':fields.boolean('DeAct Reconciled'),
                'dsr_react_date':fields.date('ReActivation Date'),
                'react_recon':fields.boolean('ReAct Reconciled'),
                'valid': fields.many2one('crashing.validation.flag','Valid'),
                'dsr_smd':fields.boolean('SMD'),
                'dsr_trade_inn':fields.selection([('yes','Yes'),('no','No')],'Trade-in'),
                'dsr_contract_term':fields.integer('Contract Term'),
                'dsr_temp_no':fields.char('Temporary #', size=10),
                'dsr_monthly_access':fields.float('Monthly Access'),
                'dsr_phone_purchase_type':fields.selection([('new_device','EIP'),('device_outright','Device Outright'),('sim_only','No Purchase')],'Phone Purchase'),
                'act_type':fields.selection([('Act','Sold'),('reactivation','Reactivation'),('deactivation','DeActivation')], 'Activation Type'),
                'employee_id' : fields.many2one('hr.employee','Emp'),
                'store_id':fields.many2one('sap.store', 'Store'),
                'market_id':fields.many2one('market.place', 'Market'),
                'region_id':fields.many2one('market.regions', 'Region'),
                'eip_phone_purchase':fields.boolean('EIP Phone Purchased'),
                'dsr_jump_already':fields.boolean('JUMP already on Account'),
                'dsr_phone_first':fields.many2one('phone.type.master', 'Device Type'),
                'dsr_transaction_id':fields.char('Transaction ID', size=64),
                'state':fields.selection([('draft','Draft'),('pending','Pending'),('cancel','Cancel'),('done','Done'),('void','VOID')],'State', readonly=True),
                'customer_name':fields.char('Customer Name', size=1024),
                'dealer_code':fields.char('Dealer Code', size=1024),                
                'sku_description' : fields.char('SKU Description', size=100),
                'dsr_designation_id':fields.many2one('hr.job','Designation')
		#'tmob_comments' : fields.text('Tmobile Comments'),#### field added as per the change to update the T-mobile comments
		#'valid_neutral': fields.many2one('crashing.validation.flag','Valid Non-Zero'),#### field added to be used for nonzero crash
    }
    _defaults = {
                'dsr_trans_type':'accessory',
                'state':'draft',
    }

    def onchange_emp_type(self, cr, uid, ids, dsr_emp_type):
        emp_obj = self.pool.get('dsr.employee.type')
        is_emp_upg = False
        if dsr_emp_type:
            emp_data = emp_obj.browse(cr, uid, dsr_emp_type)
            if emp_data.is_emp_upg:
                is_emp_upg = True
            return {'value':{'is_emp_upg':is_emp_upg,'dsr_p_number':False}}
        return {'value':{'is_emp_upg':is_emp_upg,'dsr_p_number':False}}

    def onchange_phone(self, cr, uid, ids, phone):
        if phone:
            phone_check(phone)
            return {}
        return {}

    def onchange_sku_select(self, cr, uid, ids, dsr_sku_select):
        sku_master = self.pool.get('wireless.acc.sku.master')
        if dsr_sku_select:
            cur_sku_master_obj = sku_master.browse(cr, uid, dsr_sku_select)
            return {'value': {'dsr_acc_comm': cur_sku_master_obj.acc_commission,'sku_description' : cur_sku_master_obj.acc_description}}
        return {'value': {'dsr_acc_comm':False,'sku_description':False}}

    def create(self, cr, uid, vals, context=None):
        sku_obj = self.pool.get('wireless.acc.sku.master')
        if vals['dsr_phone_no']:
            phone = vals['dsr_phone_no']
            phone_check(phone)
        sku_data = sku_obj.browse(cr, uid, vals['dsr_sku_select'])
        sku_max_qty = sku_data.acc_qty
        if vals['dsr_quantity'] < 0.00:
            raise osv.except_osv(('Error!!'),('Accessory quantity cannot be negative.'))
        elif vals['dsr_quantity'] == 0.00:
            raise osv.except_osv(('Error!!'),('Accessory quantity cannot be 0.'))
        elif vals['dsr_quantity'] > sku_max_qty:
            raise osv.except_osv(('Error!!'),('Accessory quantity cannot exceed from %s'%(sku_max_qty,)))
        if vals['dsr_list_price'] < 0.00:
            raise osv.except_osv(('Error!!'),('Accessory MRP cannot be negative.'))
        elif vals['dsr_list_price'] == 0.00:
            raise osv.except_osv(('Error!!'),('Accessory MRP cannot be 0.'))
        res = super(wireless_dsr_acc_line, self).create(cr, uid, vals, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        sku_obj = self.pool.get('wireless.acc.sku.master')
        self_obj = self.browse(cr, uid, ids[0])
        if 'dsr_sku_select' in vals:
            dsr_sku_select = vals['dsr_sku_select']
        else:
            dsr_sku_select = self_obj.dsr_sku_select.id
        sku_data = sku_obj.browse(cr, uid, dsr_sku_select)
        sku_max_qty = sku_data.acc_qty
        if 'dsr_phone_no' in vals:
            phone = vals['dsr_phone_no']
            phone_check(phone)
        if 'dsr_quantity' in vals:
            dsr_quantity = vals['dsr_quantity']
        else:
            dsr_quantity = self_obj.dsr_quantity
        if 'dsr_list_price' in vals:
            dsr_list_price = vals['dsr_list_price']
        else:
            dsr_list_price = self_obj.dsr_list_price
        if 'dsr_sku_select' not in vals:
            acc_comm = self_obj.dsr_sku_select.acc_commission
            vals.update({'dsr_acc_comm':acc_comm})
        if dsr_quantity < 0.00:
            raise osv.except_osv(('Error!!'),('Accessory quantity cannot be negative.'))
        elif dsr_quantity == 0.00:
            raise osv.except_osv(('Error!!'),('Accessory quantity cannot be 0.'))
        elif dsr_quantity > sku_max_qty:
            raise osv.except_osv(('Error!!'),('Accessory quantity cannot exceed from %s'%(sku_max_qty,)))
        if dsr_list_price < 0.00:
            raise osv.except_osv(('Error!!'),('Accessory MRP cannot be negative.'))
        elif dsr_list_price == 0.00:
            raise osv.except_osv(('Error!!'),('Accessory MRP cannot be 0.'))
        res = super(wireless_dsr_acc_line, self).write(cr, uid, ids, vals, context=context)
        return res
        
wireless_dsr_acc_line()

### code to set the accessory master at the end
class wireless_acc_sku_master(osv.osv):

    _name = 'wireless.acc.sku.master'

    _columns = {
                'categ' : fields.char('Category',size=30),
                'acc_sku' : fields.char('SKU', size=40, required="1"),
                'acc_description' : fields.char('Description', size=80,required="1"),
                'acc_commission' : fields.float('Commission'),
                'acc_qty':fields.integer('Quantity Per Line'),
                ######### field below added to add the device type to the accessory master
                'device_specific' : fields.char('Device Specification',size=40),
                'non_comm':fields.boolean('Non-Commissionable'),
                'active':fields.boolean('Active'),
                'start_date':fields.date('Start Date',required="1"),
                'end_date':fields.date('End Date',required="1")
    }
    
    _rec_name = 'acc_sku'

    _defaults = {
                'active':True,
                'acc_qty':5
    }

    _sql_constraints = []

    def create(self, cr, uid, vals, context=None):
        acc_sku = vals.get('acc_sku')
        start_date = vals.get('start_date')
        end_date = vals.get('end_date')
        if end_date < start_date:
            raise osv.except_osv(('Warning!!'),('Start Date should be greater than End Date.'))
        if acc_sku:
            acc_sku = acc_sku.strip()
            vals['acc_sku'] = acc_sku
        search_ids = self.search(cr, uid, [('acc_sku','=',acc_sku),('end_date','>=',start_date),('start_date','<=',end_date)])
        if search_ids:
            raise osv.except_osv(('Error!!'),('Accessory SKU %s is already active in system.'%(acc_sku)))
        res = super(wireless_acc_sku_master, self).create(cr, uid, vals, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        acc_data = self.browse(cr, uid, ids[0])
        if 'acc_sku' in vals:
            acc_sku = vals['acc_sku']
            acc_sku = acc_sku.strip()
            vals['acc_sku'] = acc_sku
        else:
            acc_sku = acc_data.acc_sku
            acc_sku = acc_sku.strip()
        start_date = vals.get('start_date')
        end_date = vals.get('end_date')
        if not start_date:
            start_date = acc_data.start_date
        if not end_date:
            end_date = acc_data.end_date
        search_ids = self.search(cr, uid, [('acc_sku','=',acc_sku),('end_date','>=',start_date),('start_date','<=',end_date),('id','!=',ids[0])])
        if search_ids:
            raise osv.except_osv(('Error!!'),('Accessory SKU %s is already active in system.'%(acc_sku)))
        res = super(wireless_acc_sku_master, self).write(cr, uid, ids, vals, context=context)
        return res

wireless_acc_sku_master()

### code ends here

### code ends here
############## Prepaid Line One2Many ###############################
class wireless_dsr_prepaid_line(osv.osv):
    _name = 'wireless.dsr.prepaid.line'
    _description = "Wireless DSR Prepaid Line"
    _order = 'id desc'

    def _calculate_rev(self, cr, uid, revenue_id, phone_purchase, product, tac_ids, imei):
        val = {}
        tac_master_ids = []
        spiff_no_consider = False
        revenue_obj = self.pool.get('revenue.generate.master')
        product_obj = self.pool.get('product.product')
        tac_obj = self.pool.get('tac.code.master')
        mul_factor = revenue_obj.browse(cr, uid, revenue_id).dsr_revenue_calc
        spiff_factor = revenue_obj.browse(cr, uid, revenue_id).dsr_phone_spiff
        added_rev = revenue_obj.browse(cr, uid, revenue_id).dsr_added_rev
        bonus_line_spiff = revenue_obj.browse(cr, uid, revenue_id).bonus_line_spiff
        bonus_handset_spiff = revenue_obj.browse(cr, uid, revenue_id).bonus_handset_spiff
        month_acc = product_obj.browse(cr, uid, product).monthly_access
        val = {
                'comm':0.00,
                'spiff':0.00,
                'added':0.00,
                'tot':0.00
            }        
        val['spiff'] = (spiff_factor * month_acc) + bonus_handset_spiff 
        val['comm'] = (mul_factor * month_acc) + bonus_line_spiff
        val['added'] = added_rev

        if tac_ids and imei:
            for tac_id in tac_ids:
                if tac_id:
                    tac_master_ids.append(tac_id[0])
        if tac_master_ids and imei:
            for tac_data in tac_obj.browse(cr, uid, tac_master_ids):
                if imei[:8] == tac_data.tac_code:
                    spiff_no_consider = True

        if phone_purchase == 'device_outright':
            if spiff_no_consider:
                val['tot'] = val['comm'] + val['added']
                val['spiff'] = 0
            else:
                val['tot'] = val['comm'] + val['added'] + val['spiff']
        else:
            val['tot'] = val['comm'] + val['added']
            val['spiff'] = 0.00
        return val

    def _calculate_revenue(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        rev_root_code_prod_ids = []
        rev_root_code_ids = []
        line = self.browse(cr, uid, ids[0], context=context)
        revenue_obj = self.pool.get('revenue.generate.master')
        product_obj = self.pool.get('product.product')
        res[line.id] = {
                'dsr_rev_gen': 0.00,
                'dsr_comm_amnt':0.00,
                'dsr_comm_spiff':0.00,
                'dsr_comm_added':0.00,
                'dsr_comm_per_line':0.00
            }
        product_type = line.dsr_product_type.id
        interval_type = 'at_act'
        product = line.dsr_product_description.id
        prod_code_type = self.pool.get('product.product').browse(cr, uid, product).dsr_prod_code_type.id
        phone_purchase = line.dsr_phone_purchase_type
        dsr_id = line.product_id.id
        dsr_data = self.pool.get('wireless.dsr').browse(cr, uid, dsr_id)
        trans_date = dsr_data.dsr_date
        imei = line.dsr_imei_no
        emp_des = dsr_data.dsr_designation_id.id
        comm_percent = 0.00
        base_comm_obj = self.pool.get('comm.basic.commission.formula')
        base_comm_search = base_comm_obj.search(cr, uid, [('comm_designation','=',emp_des),('comm_start_date','<=',trans_date),('comm_end_date','>=',trans_date),('comm_inactive','=',False)])
        if base_comm_search:
            comm_percent = base_comm_obj.browse(cr, uid, base_comm_search[0]).comm_percent
        else:
            base_comm_search = base_comm_obj.search(cr, uid, [('comm_start_date','<=',trans_date),('comm_end_date','>=',trans_date),('comm_inactive','=',False)])
            if base_comm_search:
                comm_percent = base_comm_obj.browse(cr, uid, base_comm_search[0]).comm_percent
        rev_root_ids = revenue_obj.search(cr, uid, [('dsr_prod_type','=',product_type),('dsr_start_date','<=',trans_date),('dsr_end_date','>=',trans_date),('inactive','=',False)])
        comm_percent = 10.00
        if rev_root_ids:
            for rev_root_id in rev_root_ids:
                rev_root_code_search = revenue_obj.search(cr, uid, [('id','=',rev_root_id),('dsr_prod_code_type','=',prod_code_type)])
                for ids in rev_root_code_search:
                    rev_root_code_ids.append(ids)
            if rev_root_code_ids:
                for rev_root_code_id in rev_root_code_ids:
                    rev_root_code_prod_search = revenue_obj.search(cr, uid, [('id','=',rev_root_code_id),('dsr_rev_product','=',product)])
                    for ids in rev_root_code_prod_search:
                        rev_root_code_prod_ids.append(ids)
                if rev_root_code_prod_ids:
                    ### Change of not considering handset spiff on excluded TAC Code List ######
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(rev_root_code_prod_ids[0]))
                    tac_ids = cr.fetchall()
                    val = self._calculate_rev(cr, uid, rev_root_code_prod_ids[0], phone_purchase, product, tac_ids, imei)
                    res[line.id]['dsr_rev_gen'] = val['tot']
                    res[line.id]['dsr_comm_per_line'] = float(res[line.id]['dsr_rev_gen'] * comm_percent / 100)
                    res[line.id]['dsr_comm_amnt'] = val['comm']
                    res[line.id]['dsr_comm_spiff'] = val['spiff']
                    res[line.id]['dsr_comm_added'] = val['added']
                    return res
                else:
                    ### Change of not considering handset spiff on excluded TAC Code List ######
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(rev_root_code_ids[0]))
                    tac_ids = cr.fetchall()
                    val = self._calculate_rev(cr, uid, rev_root_code_ids[0], phone_purchase, product, tac_ids, imei)
                    res[line.id]['dsr_rev_gen'] = val['tot']
                    res[line.id]['dsr_comm_per_line'] = float(res[line.id]['dsr_rev_gen'] * comm_percent / 100)
                    res[line.id]['dsr_comm_amnt'] = val['comm']
                    res[line.id]['dsr_comm_spiff'] = val['spiff']
                    res[line.id]['dsr_comm_added'] = val['added']
                    return res
            else:
                rev_base_ids = revenue_obj.search(cr, uid, [('dsr_prod_type','=',product_type),('dsr_start_date','<=',trans_date),('dsr_end_date','>=',trans_date),('dsr_prod_code_type','=',False),('dsr_credit_class_type','=',False),('dsr_rev_product','=',False),('dsr_activation_type','=',False),('inactive','=',False)])
                for rev_root_code_id in rev_root_ids:
                    rev_root_code_prod_search = revenue_obj.search(cr, uid, [('id','=',rev_root_code_id),('dsr_rev_product','=',product)])
                    for ids in rev_root_code_prod_search:
                        rev_root_code_prod_ids.append(ids)
                if rev_root_code_prod_ids:
                    ### Change of not considering handset spiff on excluded TAC Code List ######
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(rev_root_code_prod_ids[0]))
                    tac_ids = cr.fetchall()
                    val = self._calculate_rev(cr, uid, rev_root_code_prod_ids[0], phone_purchase, product, tac_ids, imei)
                    res[line.id]['dsr_rev_gen'] = val['tot']
                    res[line.id]['dsr_comm_per_line'] = float(res[line.id]['dsr_rev_gen'] * comm_percent / 100)
                    res[line.id]['dsr_comm_amnt'] = val['comm']
                    res[line.id]['dsr_comm_spiff'] = val['spiff']
                    res[line.id]['dsr_comm_added'] = val['added']
                    return res                
                elif rev_base_ids:
                    ### Change of not considering handset spiff on excluded TAC Code List ######
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(rev_base_ids[0]))
                    tac_ids = cr.fetchall()
                    val = self._calculate_rev(cr, uid, rev_base_ids[0], phone_purchase, product, tac_ids, imei)
                    res[line.id]['dsr_rev_gen'] = val['tot']
                    res[line.id]['dsr_comm_per_line'] = float(res[line.id]['dsr_rev_gen'] * comm_percent / 100)
                    res[line.id]['dsr_comm_amnt'] = val['comm']
                    res[line.id]['dsr_comm_spiff'] = val['spiff']
                    res[line.id]['dsr_comm_added'] = val['added']
                    return res
                else:#condition given by shreyas
                ############# changes done be Krishna #############
                    #pass
                    res[line.id]['dsr_rev_gen'] = 0.00
                    res[line.id]['dsr_comm_per_line'] = 0.00
                    res[line.id]['dsr_comm_amnt'] = 0.00
                    res[line.id]['dsr_comm_spiff'] = 0.00
                    res[line.id]['dsr_comm_added'] = 0.00
                    return res
                # else:
                #     raise osv.except_osv(('Error!!!'),('There is no base revenue formula for Prepaid is defined. Please contact Administrator.'))
        else:#condition given by shreyas
            ############# changes done be Krishna #############
            #pass
            res[line.id]['dsr_rev_gen'] = 0.00
            res[line.id]['dsr_comm_per_line'] = 0.00
            res[line.id]['dsr_comm_amnt'] = 0.00
            res[line.id]['dsr_comm_spiff'] = 0.00
            res[line.id]['dsr_comm_added'] = 0.00
            return res        
        # else:
        #     raise osv.except_osv(('Error!!!'),('There is no base revenue formula for Prepaid is defined. Please contact Administrator.'))
    
    def _calculate_revenue_line(self, cr, uid, ids, product, product_type, prod_code_type):
        res = {}
        rev_root_code_prod_ids = []
        rev_root_code_ids = []
        line = self.browse(cr, uid, ids)
        revenue_obj = self.pool.get('revenue.generate.master')
        product_obj = self.pool.get('product.product')
        res[line.id] = {
                'dsr_rev_gen': 0.00,
            }
        phone_purchase = line.dsr_phone_purchase_type
        imei = line.dsr_imei_no
        dsr_id = line.product_id.id
        trans_date = self.pool.get('wireless.dsr').browse(cr, uid, dsr_id).dsr_date
        rev_root_ids = revenue_obj.search(cr, uid, [('dsr_prod_type','=',product_type),('dsr_start_date','<=',trans_date),('dsr_end_date','>=',trans_date),('inactive','=',False)])
        if rev_root_ids:
            for rev_root_id in rev_root_ids:
                rev_root_code_search = revenue_obj.search(cr, uid, [('id','=',rev_root_id),('dsr_prod_code_type','=',prod_code_type)])
                for ids in rev_root_code_search:
                    rev_root_code_ids.append(ids)
            if rev_root_code_ids:
                for rev_root_code_id in rev_root_code_ids:
                    rev_root_code_prod_search = revenue_obj.search(cr, uid, [('id','=',rev_root_code_id),('dsr_rev_product','=',product)])
                    for ids in rev_root_code_prod_search:
                        rev_root_code_prod_ids.append(ids)
                if rev_root_code_prod_ids:
                    ### Change of not considering handset spiff on excluded TAC Code List ######
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(rev_root_code_prod_ids[0]))
                    tac_ids = cr.fetchall()
                    val = self._calculate_rev(cr, uid, rev_root_code_prod_ids[0], phone_purchase, product, tac_ids, imei)
                    return val
                else:
                    ### Change of not considering handset spiff on excluded TAC Code List ######
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(rev_root_code_ids[0]))
                    tac_ids = cr.fetchall()
                    val = self._calculate_rev(cr, uid, rev_root_code_ids[0], phone_purchase, product, tac_ids, imei)
                    return val
            else:
                rev_base_ids = revenue_obj.search(cr, uid, [('dsr_prod_type','=',product_type),('dsr_start_date','<=',trans_date),('dsr_end_date','>=',trans_date),('dsr_prod_code_type','=',False),('dsr_credit_class_type','=',False),('dsr_rev_product','=',False),('dsr_activation_type','=',False),('inactive','=',False)])
                for rev_root_code_id in rev_root_ids:
                    rev_root_code_prod_search = revenue_obj.search(cr, uid, [('id','=',rev_root_code_id),('dsr_rev_product','=',product)])
                    for ids in rev_root_code_prod_search:
                        rev_root_code_prod_ids.append(ids)
                if rev_root_code_prod_ids:
                    ### Change of not considering handset spiff on excluded TAC Code List ######
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(rev_root_code_prod_ids[0]))
                    tac_ids = cr.fetchall()
                    val = self._calculate_rev(cr, uid, rev_root_code_prod_ids[0], phone_purchase, product, tac_ids, imei)
                    return val
                elif rev_base_ids:
                    ### Change of not considering handset spiff on excluded TAC Code List ######
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(rev_base_ids[0]))
                    tac_ids = cr.fetchall()
                    val = self._calculate_rev(cr, uid, rev_base_ids[0], phone_purchase, product, tac_ids, imei)
                    return val
                else:#condition given by shreyas
                ############# changes done be Krishna #############
                    #pass
                    #res[line.id]['dsr_rev_gen'] = 0.00
                    #res[line.id]['dsr_comm_per_line'] = 0.00
                    #res[line.id]['dsr_comm_amnt'] = 0.00
                    #res[line.id]['dsr_comm_spiff'] = 0.00
                    #res[line.id]['dsr_comm_added'] = 0.00
                    val = 0
                    return val
                # else:
                #     raise osv.except_osv(('Error!!!'),('There is no base revenue formula for Prepaid is defined. Please contact Administrator.'))
        else:#condition given by shreyas
            ############# changes done be Krishna #############
            #pass
            #res[line.id]['dsr_rev_gen'] = 0.00
            #res[line.id]['dsr_comm_per_line'] = 0.00
            #res[line.id]['dsr_comm_amnt'] = 0.00
            #res[line.id]['dsr_comm_spiff'] = 0.00
            #res[line.id]['dsr_comm_added'] = 0.00
            val = 0
            return val
        # else:
        #     raise osv.except_osv(('Error!!!'),('There is no base revenue formula for Prepaid is defined. Please contact Administrator.'))

    def _calculate_total_prepaid_revenue(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        pre_search_ids = self.search(cr, uid, [('created_feature','=',False)])
        for line in self.browse(cr, uid, ids, context=context):
            product_obj = self.pool.get('product.product')
            dsr_id = line.product_id.id
            dsr_data = self.pool.get('wireless.dsr').browse(cr, uid, dsr_id)
            trans_date = dsr_data.dsr_date
            emp_des = dsr_data.dsr_designation_id.id
            comm_percent = 0.00
            base_comm_obj = self.pool.get('comm.basic.commission.formula')
            base_comm_search = base_comm_obj.search(cr, uid, [('comm_designation','=',emp_des),('comm_start_date','<=',trans_date),('comm_end_date','>=',trans_date),('comm_inactive','=',False)])
            if base_comm_search:
                comm_percent = base_comm_obj.browse(cr, uid, base_comm_search[0]).comm_percent
            else:
                base_comm_search = base_comm_obj.search(cr, uid, [('comm_start_date','<=',trans_date),('comm_end_date','>=',trans_date),('comm_inactive','=',False)])
                if base_comm_search:
                    comm_percent = base_comm_obj.browse(cr, uid, base_comm_search[0]).comm_percent
            res[line.id] = {
                            'dsr_tot_rev_gen':0.00,
                            'dsr_tot_comm_per_line':0.00
                        }
            val = 0.00
            product = line.dsr_product_description.id
            prod_data = product_obj.browse(cr, uid, product)
            product_type = prod_data.categ_id.id
            prod_code_type = prod_data.dsr_prod_code_type.id
            val1 = self._calculate_revenue_line(cr, uid, line.id, product, product_type, prod_code_type)
            val = val + val1['tot']
            if line.dsr_talk_n_text == True:
                product = line.dsr_talk_soc.id
                if not product:
                    product = product_obj.search(cr, uid, [('dsr_categ_id','=','prepaid'),('is_intl','=',True)])[0]
                prod_data = product_obj.browse(cr, uid, product)
                product_type = prod_data.categ_id.id
                prod_code_type = prod_data.dsr_prod_code_type.id
                val1 = self._calculate_revenue_line(cr, uid, line.id, product, product_type, prod_code_type)
                val = val + val1['tot']
            if line.dsr_tether == True:
                product = line.dsr_tether_soc.id
                if not product:
                    product = product_obj.search(cr, uid, [('dsr_categ_id','=','prepaid'),('is_tether','=',True)])[0]
                prod_data = product_obj.browse(cr, uid, product)
                product_type = prod_data.categ_id.id
                prod_code_type = prod_data.dsr_prod_code_type.id
                val1 = self._calculate_revenue_line(cr, uid, line.id, product, product_type, prod_code_type)
                val = val + val1['tot']
            if line.dsr_php == True:
                product = line.dsr_php_soc.id
                if not product:
                    product = product_obj.search(cr, uid, [('dsr_categ_id','=','prepaid'),('is_php','=',True)])[0]
                prod_data = product_obj.browse(cr, uid, product)
                product_type = prod_data.categ_id.id
                prod_code_type = prod_data.dsr_prod_code_type.id
                val1 = self._calculate_revenue_line(cr, uid, line.id, product, product_type, prod_code_type)
                val = val + val1['tot']
            if line.dsr_score == True:
                product = line.dsr_score_soc.id
                if not product:
                    product = product_obj.search(cr, uid, [('dsr_categ_id','=','prepaid'),('is_score','=',True)])[0]
                prod_data = product_obj.browse(cr, uid, product)
                product_type = prod_data.categ_id.id
                prod_code_type = prod_data.dsr_prod_code_type.id
                val1 = self._calculate_revenue_line(cr, uid, line.id, product, product_type, prod_code_type)
                val = val + val1['tot']
            res[line.id]['dsr_tot_rev_gen'] = val
            res[line.id]['dsr_tot_comm_per_line'] = float(val * comm_percent / 100)
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('wireless.dsr.prepaid.line').browse(cr, uid, ids, context=context):
            result[line.id] = True
        return result.keys()

    _columns = {
                'product_id':fields.many2one('wireless.dsr','Product Id'),
                'dsr_trans_type':fields.selection(_prod_type, 'Transaction Type'),
                'dsr_product_type':fields.many2one('product.category','Product Type'),
                'dsr_product_code_type':fields.many2one('product.category','Product Code Type'),
                'dsr_product_code':fields.char('Product Code', size=64),                
                'dsr_product_description':fields.many2one('product.product', 'Product Description'),
                'dsr_sim_no': fields.char('SIM #', size=25),
                'dsr_imei_no':fields.char('IMEI #', size=15),
                'dsr_phone_no':fields.char('Mobile Phone', size=10),
                'dsr_rev_gen':fields.function(_calculate_revenue, string="Total Amount", type='float', multi='sums',
                        store={
                                'wireless.dsr.prepaid.line': (_get_order, [], 10),
                }),
                'dsr_comm_amnt':fields.function(_calculate_revenue, string="DSR Commission Amount", type='float', multi='sums',
                        store={
                                'wireless.dsr.prepaid.line': (_get_order, [], 10),
                }),
                'dsr_comm_spiff':fields.function(_calculate_revenue, string="DSR Spiff Amount", type='float', multi='sums',
                        store={
                                'wireless.dsr.prepaid.line': (_get_order, [], 10),
                }),
                'dsr_comm_added':fields.function(_calculate_revenue, string="DSR Added Amount", type='float', multi='sums',
                        store={
                                'wireless.dsr.prepaid.line': (_get_order, [], 10),
                }),
                'dsr_comm_per_line':fields.function(_calculate_revenue, string="Commission per line", type='float', multi='sums',
                    store={
                                'wireless.dsr.prepaid.line': (_get_order, [], 10),
                }),
                'act_type':fields.selection([('Act','Activation'),('reactivation','Reactivation'),('deactivation','DeActivation')], 'Activation Type'),
                'dsr_phone_purchase_type':fields.selection([('sim_only','SIM Only'),('device_outright','Device Outright')],'Phone Purchase'),
                'dsr_talk_n_text':fields.boolean('Intl Talk n Text'),
                'dsr_talk_soc':fields.many2one('product.product', 'Intl Talk n Text Description'),
                'dsr_tether':fields.boolean('Tether'),
                'dsr_tether_soc':fields.many2one('product.product', 'Tether Description'),
                'dsr_php':fields.boolean('PHP'),
                'dsr_php_soc':fields.many2one('product.product', 'PHP Description'),
                'dsr_score':fields.boolean('SCORE'),
                'dsr_score_soc':fields.many2one('product.product', 'Score Description'),
                'created_feature':fields.boolean('Created Feature'),
                'dsr_act_date':fields.date('Activation Date'),
                'pseudo_date':fields.date('Pseudo Transaction Date'),
                'dsr_deact_date':fields.date('DeActivation Date'),
                'act_recon':fields.boolean('Act Reconciled'),
                'deact_recon':fields.boolean('DeAct Reconciled'),
                'dsr_react_date':fields.date('ReActivation Date'),
                'react_recon':fields.boolean('ReAct Reconciled'),
                'valid': fields.many2one('crashing.validation.flag','Valid'),
                'dsr_smd':fields.boolean('SMD'),
                'dsr_trade_inn':fields.selection([('yes','Yes'),('no','No')],'Trade-in'),
                'dsr_contract_term':fields.integer('Contract Term'),
                'dsr_temp_no':fields.char('Temporary #', size=10),
                'dsr_monthly_access':fields.float('Monthle Access'),
                'dsr_cust_ban_no':fields.char('BAN #', size=124),
                'dsr_tot_rev_gen':fields.function(_calculate_total_prepaid_revenue, string="Total Rev Gen.", type='float', multi='sums'),
                'dsr_tot_comm_per_line':fields.function(_calculate_total_prepaid_revenue, string="Total Commission per line", type='float', multi='sums'),
                'dsr_pmd': fields.boolean('PMD'),
                'comments': fields.text('Reasons For Deactivation of Chargebacks'),
                'noncommissionable':fields.boolean('Non Commissionable'),
                'spiff_amt': fields.float('Spiff Amt'),
                'commission_amt': fields.float('Commissions Amt'),
                'crash_act_date': fields.date('Crashing Activation Date'),
                'crash_deact_date': fields.date('Crashing Deactivation Date'),
                'crash_react_date': fields.date('Crashing Reactivation Date'),
                'employee_id' : fields.many2one('hr.employee','Emp'),
                'store_id':fields.many2one('sap.store', 'Store'),
                'market_id':fields.many2one('market.place', 'Market'),
                'region_id':fields.many2one('market.regions', 'Region'),
                'eip_phone_purchase':fields.boolean('EIP Phone Purchased'),
                'dsr_jump_already':fields.boolean('JUMP already on Account'),
                'dsr_phone_first':fields.boolean('Device Type'),
                'dsr_phone_first':fields.many2one('phone.type.master', 'Device Type'),
                'dsr_transaction_id':fields.char('Transaction ID', size=64),
                'state':fields.selection([('draft','Draft'),('pending','Pending'),('cancel','Cancel'),('done','Done'),('void','VOID')],'State', readonly=True),
                'customer_name':fields.char('Customer Name', size=1024),
                'dealer_code':fields.char('Dealer Code', size=1024),
                'prepaid_id':fields.many2one('wireless.dsr.prepaid.line','Prepaid Id'),
                'is_act':fields.boolean('Activation'),
                'pre_is_intl':fields.boolean('Pre Intl Text'),
                'pre_is_tether':fields.boolean('Pre Tether'),
                'pre_is_php':fields.boolean('Pre PHP'),
                'pre_is_score':fields.boolean('Pre Score'),
                'dsr_exception':fields.boolean('Exception'),
                'dsr_designation_id':fields.many2one('hr.job','Designation')
		#'tmob_comments' : fields.text('Tmobile Comments'),#### field added as per the change to update the T-mobile comments
		#'valid_neutral': fields.many2one('crashing.validation.flag','Valid Non-Zero'),#### field added to be used for nonzero crash
    }
    _defaults = {
                'act_type':'Act',
                'state':'draft',
                'dsr_trans_type':'prepaid',
                'created_feature':False,
                'dsr_exception':False
    }

    def onchange_product(self, cr, uid, ids, product):
        prod_obj = self.pool.get('product.product')
        if product:
            prod_data = prod_obj.browse(cr, uid, product)
            product_soc = prod_data.default_code
            prod_code_type = prod_data.dsr_prod_code_type.id
            monthly_access = prod_data.monthly_access
            contract_term = prod_data.contract_term
            is_intl = prod_data.is_intl
            is_tether = prod_data.is_tether
            is_php = prod_data.is_php
            is_score = prod_data.is_score
            if is_intl or is_tether or is_php or is_score:
                if is_intl:
                    pre_is_intl = True
                    pre_is_php = False
                    pre_is_tether = False
                    pre_is_score = False
                elif is_php:
                    pre_is_php = True
                    pre_is_intl = False
                    pre_is_tether = False
                    pre_is_score = False
                elif is_tether:
                    pre_is_tether = True
                    pre_is_php = False
                    pre_is_intl = False
                    pre_is_score = False
                elif is_score:
                    pre_is_score = True
                    pre_is_php = False
                    pre_is_tether = False
                    pre_is_intl = False
                is_act = False
            else:
                is_act = True
                pre_is_intl = False
                pre_is_php = False
                pre_is_tether = False
                pre_is_score = False
            return {'value': {'dsr_product_code' : product_soc,
                            'dsr_product_code_type':prod_code_type,
                            'dsr_monthly_access':monthly_access,
                            'dsr_contract_term':contract_term,
                            'is_act':is_act,
                            'pre_is_intl':pre_is_intl,
                            'pre_is_score':pre_is_score,
                            'pre_is_php':pre_is_php,
                            'pre_is_tether':pre_is_tether,
                            'dsr_talk_n_text':False,
                            'dsr_talk_soc':False,
                            'dsr_tether':False,
                            'dsr_tether_soc':False,
                            'dsr_php':False,
                            'dsr_php_soc':False,
                            'dsr_score':False,
                            'dsr_score_soc':False}}
        return {'value':{
                        'dsr_product_code':False,
                        'dsr_product_code_type':False,
                        'dsr_monthly_access':False,
                        'dsr_contract_term':False,
                        'is_act':False,
                        'pre_is_intl':False,
                        'pre_is_score':False,
                        'pre_is_php':False,
                        'pre_is_tether':False,
                        'dsr_talk_n_text':False,
                        'dsr_talk_soc':False,
                        'dsr_tether':False,
                        'dsr_tether_soc':False,
                        'dsr_php':False,
                        'dsr_php_soc':False,
                        'dsr_score':False,
                        'dsr_score_soc':False
        }}

    def onchange_product_type(self, cr, uid, ids, product_type):
        if product_type:
            return {'value': {'dsr_product_description' : False}}
        return {}

    def onchange_phone(self, cr, uid, ids, phone):
        if phone:
            phone_check(phone)
            return {}
        return {}

    def onchange_talk(self, cr, uid, ids, talk):
        if not talk:
            return {'value':{'dsr_talk_soc':False}}
        return {}

    def onchange_tether(self, cr, uid, ids, tether):
        if not tether:
            return {'value':{'dsr_tether_soc':False}}
        return {}

    def onchange_php(self, cr, uid, ids, php):
        if not php:
            return {'value':{'dsr_php_soc':False}}
        return {}

    def onchange_score(self, cr, uid, ids, score):
        if not score:
            return {'value':{'dsr_score_soc':False}}
        return {}

    def onchange_sim(self, cr, uid, ids, sim):
        if sim:
            sim_validation(sim)
            return {}
        return {}

    def onchange_imei(self, cr, uid, ids, imei, dsr_phone_purchase_type):
        if imei and (dsr_phone_purchase_type != 'sim_only'):
            imei_check_prepaid(imei)
            return {}
        return {}

    def create_feature_lines(self, cr, uid, vals, res):
        prod_obj = self.pool.get('product.product')
        if vals['dsr_talk_n_text'] and vals['dsr_talk_soc']:
            prod_data = prod_obj.browse(cr, uid, vals['dsr_talk_soc'])
            intl_data = {
                        'product_id':vals['product_id'],
                        'dsr_product_type':prod_data.categ_id.id,
                        'dsr_product_code':prod_data.default_code,
                        'dsr_product_code_type':prod_data.dsr_prod_code_type.id,
                        'dsr_monthly_access':prod_data.monthly_access,
                        'dsr_contract_term':prod_data.contract_term,
                        'dsr_product_description':prod_data.id,
                        'dsr_phone_no':vals['dsr_phone_no'],
                        'dsr_sim_no':vals['dsr_sim_no'],
                        'dsr_imei_no':vals['dsr_imei_no'],
                        'dsr_phone_purchase_type':vals['dsr_phone_purchase_type'],
                        'dsr_talk_n_text':False,
                        'dsr_tether':False,
                        'dsr_php':False,
                        'dsr_score':False,
                        'created_feature':True,
                        'prepaid_id':res,
                        'is_act':False,
                        'pre_is_intl':True,
                        'pre_is_score':False,
                        'pre_is_php':False,
                        'pre_is_tether':False
            }
            self.create(cr, uid, intl_data)
        if vals['dsr_tether'] and vals['dsr_tether_soc']:
            prod_data = prod_obj.browse(cr, uid, vals['dsr_tether_soc'])
            tether_data = {
                        'dsr_product_type':prod_data.categ_id.id,
                        'product_id':vals['product_id'],
                        'dsr_product_code':prod_data.default_code,
                        'dsr_product_code_type':prod_data.dsr_prod_code_type.id,
                        'dsr_monthly_access':prod_data.monthly_access,
                        'dsr_contract_term':prod_data.contract_term,
                        'dsr_product_description':prod_data.id,
                        'dsr_phone_no':vals['dsr_phone_no'],
                        'dsr_sim_no':vals['dsr_sim_no'],
                        'dsr_imei_no':vals['dsr_imei_no'],
                        'dsr_phone_purchase_type':vals['dsr_phone_purchase_type'],
                        'dsr_talk_n_text':False,
                        'dsr_tether':False,
                        'dsr_php':False,
                        'dsr_score':False,
                        'created_feature':True,
                        'prepaid_id':res,
                        'is_act':False,
                        'pre_is_intl':False,
                        'pre_is_score':False,
                        'pre_is_php':False,
                        'pre_is_tether':True
            }
            self.create(cr, uid, tether_data)
        if vals['dsr_php'] and vals['dsr_php_soc']:
            prod_data = prod_obj.browse(cr, uid, vals['dsr_php_soc'])
            php_data = {
                        'dsr_product_type':prod_data.categ_id.id,
                        'product_id':vals['product_id'],
                        'dsr_product_code':prod_data.default_code,
                        'dsr_product_code_type':prod_data.dsr_prod_code_type.id,
                        'dsr_monthly_access':prod_data.monthly_access,
                        'dsr_contract_term':prod_data.contract_term,
                        'dsr_product_description':prod_data.id,
                        'dsr_phone_no':vals['dsr_phone_no'],
                        'dsr_sim_no':vals['dsr_sim_no'],
                        'dsr_imei_no':vals['dsr_imei_no'],
                        'dsr_phone_purchase_type':vals['dsr_phone_purchase_type'],
                        'dsr_talk_n_text':False,
                        'dsr_tether':False,
                        'dsr_php':False,
                        'dsr_score':False,
                        'created_feature':True,
                        'prepaid_id':res,
                        'is_act':False,
                        'pre_is_intl':False,
                        'pre_is_score':False,
                        'pre_is_php':True,
                        'pre_is_tether':False
            }
            self.create(cr, uid, php_data)
        if vals['dsr_score'] and vals['dsr_score_soc']:
            prod_data = prod_obj.browse(cr, uid, vals['dsr_score_soc'])
            score_data = {
                        'dsr_product_type':prod_data.categ_id.id,
                        'product_id':vals['product_id'],
                        'dsr_product_code':prod_data.default_code,
                        'dsr_product_code_type':prod_data.dsr_prod_code_type.id,
                        'dsr_monthly_access':prod_data.monthly_access,
                        'dsr_contract_term':prod_data.contract_term,
                        'dsr_product_description':prod_data.id,
                        'dsr_phone_no':vals['dsr_phone_no'],
                        'dsr_sim_no':vals['dsr_sim_no'],
                        'dsr_imei_no':vals['dsr_imei_no'],
                        'dsr_phone_purchase_type':vals['dsr_phone_purchase_type'],
                        'dsr_talk_n_text':False,
                        'dsr_tether':False,
                        'dsr_php':False,
                        'dsr_score':False,
                        'created_feature':True,
                        'prepaid_id':res,
                        'is_act':False,
                        'pre_is_intl':False,
                        'pre_is_score':True,
                        'pre_is_php':False,
                        'pre_is_tether':False
            }
            self.create(cr, uid, score_data)
        return True

    def create(self, cr, uid, vals, context=None):        
        if vals['dsr_phone_no']:
            phone = vals['dsr_phone_no']
            phone_check(phone)
        if vals['dsr_imei_no'] and vals['dsr_phone_purchase_type']:
            number = vals['dsr_imei_no']
            dsr_phone_purchase_type = vals['dsr_phone_purchase_type']
            if dsr_phone_purchase_type != 'sim_only':
                imei_check_prepaid(number)
        if vals['dsr_sim_no']:
            card_number = vals['dsr_sim_no']
            sim_validation(card_number)
        res = super(wireless_dsr_prepaid_line, self).create(cr, uid, vals, context=context)
        if (vals['dsr_talk_n_text'] and vals['dsr_talk_soc']) or (vals['dsr_tether'] and vals['dsr_tether_soc']) or (vals['dsr_php'] and vals['dsr_php_soc']) or (vals['dsr_score'] and vals['dsr_score_soc']):
            self.create_feature_lines(cr, uid, vals, res)
        # if vals['data'] or vals['intl_feature'] or vals['messaging'] or vals['other']:
        #     self._create_data_feature(cr, uid, vals)
        return res

    def update_feature_lines(self, cr, uid, ids, vals):
        prod_obj = self.pool.get('product.product')
        self_data = self.browse(cr, uid, ids[0])
        # search_ids = self.search(cr, uid, [('created_feature','=',False),('id','=',ids[0])])
        # if search_ids:
        phone = self_data.dsr_phone_no or ''
        imei = self_data.dsr_imei_no or ''
        sim = self_data.dsr_sim_no or ''
        phone_purchase = self_data.dsr_phone_purchase_type or ''
        product_id = self_data.product_id.id or False
        if 'dsr_talk_n_text' in vals:
            if vals['dsr_talk_n_text'] == False:
                intl_code = self_data.dsr_talk_soc.id
                if not intl_code:
                    intl_code = prod_obj.search(cr, uid, [('dsr_categ_id','=','prepaid'),('is_intl','=',True)])[0]
                search_intl_ids = self.search(cr, uid, [('dsr_product_description','=',intl_code),('created_feature','=',True),('prepaid_id','=',ids[0])])
                if search_intl_ids:
                    self.unlink(cr, uid, search_intl_ids)
        if 'dsr_talk_soc' in vals:
            intl_code = self_data.dsr_talk_soc.id
            search_intl_ids = self.search(cr, uid, [('dsr_product_description','=',intl_code),('created_feature','=',True),('prepaid_id','=',ids[0])])
            if search_intl_ids:
                self.unlink(cr, uid, search_intl_ids)
            if vals['dsr_talk_soc']:
                prod_data = prod_obj.browse(cr, uid, vals['dsr_talk_soc'])
                intl_data = {
                            'product_id':product_id,
                            'dsr_product_type':prod_data.categ_id.id,
                            'dsr_product_code':prod_data.default_code,
                            'dsr_product_code_type':prod_data.dsr_prod_code_type.id,
                            'dsr_monthly_access':prod_data.monthly_access,
                            'dsr_contract_term':prod_data.contract_term,
                            'dsr_product_description':prod_data.id,
                            'dsr_phone_no':phone,
                            'dsr_sim_no':sim,
                            'dsr_imei_no':imei,
                            'dsr_phone_purchase_type':phone_purchase,
                            'dsr_talk_n_text':False,
                            'dsr_tether':False,
                            'dsr_php':False,
                            'dsr_score':False,
                            'created_feature':True,
                            'prepaid_id':ids[0],
                            'is_act':False,
                            'pre_is_intl':True,
                            'pre_is_score':False,
                            'pre_is_php':False,
                            'pre_is_tether':False
                            }
                self.create(cr, uid, intl_data)
        if 'dsr_tether' in vals:
            if vals['dsr_tether'] == False:
                tether_code = self_data.dsr_tether_soc.id
                if not tether_code:
                    tether_code = prod_obj.search(cr, uid, [('dsr_categ_id','=','prepaid'),('is_tether','=',True)])[0]
                search_tether_ids = self.search(cr, uid, [('dsr_product_description','=',tether_code),('created_feature','=',True),('prepaid_id','=',ids[0])])
                if search_tether_ids:
                    self.unlink(cr, uid, search_tether_ids)
        if 'dsr_tether_soc' in vals:
            tether_code = self_data.dsr_tether_soc.id
            search_tether_ids = self.search(cr, uid, [('dsr_product_description','=',tether_code),('created_feature','=',True),('prepaid_id','=',ids[0])])
            if search_tether_ids:
                self.unlink(cr, uid, search_tether_ids)
            if vals['dsr_tether_soc']:
                prod_data = prod_obj.browse(cr, uid, vals['dsr_tether_soc'])
                tether_data = {
                            'product_id':product_id,
                            'dsr_product_type':prod_data.categ_id.id,
                            'dsr_product_code':prod_data.default_code,
                            'dsr_product_code_type':prod_data.dsr_prod_code_type.id,
                            'dsr_monthly_access':prod_data.monthly_access,
                            'dsr_contract_term':prod_data.contract_term,
                            'dsr_product_description':prod_data.id,
                            'dsr_phone_no':phone,
                            'dsr_sim_no':sim,
                            'dsr_imei_no':imei,
                            'dsr_phone_purchase_type':phone_purchase,
                            'dsr_talk_n_text':False,
                            'dsr_tether':False,
                            'dsr_php':False,
                            'dsr_score':False,
                            'created_feature':True,
                            'prepaid_id':ids[0],
                            'is_act':False,
                            'pre_is_intl':False,
                            'pre_is_score':False,
                            'pre_is_php':False,
                            'pre_is_tether':True
                            }
                self.create(cr, uid, tether_data)
        if 'dsr_php' in vals:
            if vals['dsr_php'] == False:
                php_code = self_data.dsr_php_soc.id
                if not php_code:
                    php_code = prod_obj.search(cr, uid, [('dsr_categ_id','=','prepaid'),('is_php','=',True)])[0]
                search_php_ids = self.search(cr, uid, [('dsr_product_description','=',php_code),('created_feature','=',True),('prepaid_id','=',ids[0])])
                if search_php_ids:
                    self.unlink(cr, uid, search_php_ids)
        if 'dsr_php_soc' in vals:
            php_code = self_data.dsr_php_soc.id
            search_php_ids = self.search(cr, uid, [('dsr_product_description','=',php_code),('created_feature','=',True),('prepaid_id','=',ids[0])])
            if search_php_ids:
                self.unlink(cr, uid, search_php_ids)
            if vals['dsr_php_soc']:
                prod_data = prod_obj.browse(cr, uid, vals['dsr_php_soc'])
                php_data = {
                            'product_id':product_id,
                            'dsr_product_type':prod_data.categ_id.id,
                            'dsr_product_code':prod_data.default_code,
                            'dsr_product_code_type':prod_data.dsr_prod_code_type.id,
                            'dsr_monthly_access':prod_data.monthly_access,
                            'dsr_contract_term':prod_data.contract_term,
                            'dsr_product_description':prod_data.id,
                            'dsr_phone_no':phone,
                            'dsr_sim_no':sim,
                            'dsr_imei_no':imei,
                            'dsr_phone_purchase_type':phone_purchase,
                            'dsr_talk_n_text':False,
                            'dsr_tether':False,
                            'dsr_php':False,
                            'dsr_score':False,
                            'created_feature':True,
                            'prepaid_id':ids[0],
                            'is_act':False,
                            'pre_is_intl':False,
                            'pre_is_score':False,
                            'pre_is_php':True,
                            'pre_is_tether':False
                            }
                self.create(cr, uid, php_data)
        if 'dsr_score' in vals:
            if vals['dsr_score'] == False:
                score_code = self_data.dsr_score_soc.id
                if not score_code:
                    score_code = prod_obj.search(cr, uid, [('dsr_categ_id','=','prepaid'),('is_score','=',True)])[0]
                search_score_ids = self.search(cr, uid, [('dsr_product_description','=',score_code),('created_feature','=',True),('prepaid_id','=',ids[0])])
                if search_score_ids:
                    self.unlink(cr, uid, search_score_ids)
        if 'dsr_score_soc' in vals:
            score_code = self_data.dsr_score_soc.id
            search_score_ids = self.search(cr, uid, [('dsr_product_description','=',score_code),('created_feature','=',True),('prepaid_id','=',ids[0])])
            if search_score_ids:
                self.unlink(cr, uid, search_score_ids)
            if vals['dsr_score_soc']:
                prod_data = prod_obj.browse(cr, uid, vals['dsr_score_soc'])
                score_data = {
                            'product_id':product_id,
                            'dsr_product_type':prod_data.categ_id.id,
                            'dsr_product_code':prod_data.default_code,
                            'dsr_product_code_type':prod_data.dsr_prod_code_type.id,
                            'dsr_monthly_access':prod_data.monthly_access,
                            'dsr_contract_term':prod_data.contract_term,
                            'dsr_product_description':prod_data.id,
                            'dsr_phone_no':phone,
                            'dsr_sim_no':sim,
                            'dsr_imei_no':imei,
                            'dsr_phone_purchase_type':phone_purchase,
                            'dsr_talk_n_text':False,
                            'dsr_tether':False,
                            'dsr_php':False,
                            'dsr_score':False,
                            'created_feature':True,
                            'prepaid_id':ids[0],
                            'is_act':False,
                            'pre_is_intl':False,
                            'pre_is_score':True,
                            'pre_is_php':False,
                            'pre_is_tether':False
                            }
                self.create(cr, uid, score_data)
        search_child_prepaid = self.search(cr, uid, [('created_feature','=',True),('prepaid_id','=',ids[0])])
        if 'dsr_phone_purchase_type' in vals:
            if search_child_prepaid:
                for search_child_prepaid_id in search_child_prepaid:
                    self.write(cr, uid, [search_child_prepaid_id], {'dsr_phone_purchase_type':vals['dsr_phone_purchase_type']})
        if 'dsr_imei_no' in vals:
            if search_child_prepaid:
                for search_child_prepaid_id in search_child_prepaid:
                    self.write(cr, uid, [search_child_prepaid_id], {'dsr_imei_no':vals['dsr_imei_no']})
        if 'dsr_phone_no' in vals:
            if search_child_prepaid:
                for search_child_prepaid_id in search_child_prepaid:
                    self.write(cr, uid, [search_child_prepaid_id], {'dsr_phone_no':vals['dsr_phone_no']})
        if 'dsr_sim_no' in vals:
            if search_child_prepaid:
                for search_child_prepaid_id in search_child_prepaid:
                    self.write(cr, uid, [search_child_prepaid_id], {'dsr_sim_no':vals['dsr_sim_no']})
        return True    

    def write(self, cr, uid, ids, vals, context=None):
        if 'dsr_phone_no' in vals:
            phone = vals['dsr_phone_no']
            phone_check(phone)
        if 'dsr_phone_purchase_type' in vals:
            dsr_phone_purchase_type = vals['dsr_phone_purchase_type']
            number = self.browse(cr, uid, ids[0]).dsr_imei_no
            if dsr_phone_purchase_type != 'sim_only':
                imei_check(number)
        else:
            dsr_phone_purchase_type = self.browse(cr, uid, ids[0]).dsr_phone_purchase_type
        if 'dsr_imei_no' in vals:
            number = vals['dsr_imei_no']
            if dsr_phone_purchase_type != 'sim_only':
                imei_check_prepaid(number)
        if 'dsr_sim_no' in vals:
            card_number = vals['dsr_sim_no']
            sim_validation(card_number)
        search_ids = self.search(cr, uid, [('created_feature','=',False),('id','=',ids[0])])
        if search_ids:
            self.update_feature_lines(cr, uid, ids, vals)
        res = super(wireless_dsr_prepaid_line, self).write(cr, uid, ids, vals, context=context)
        return res

    def unlink(self, cr, uid, ids, context=None):
        prod_obj = self.pool.get('product.product')
        search_ids = self.search(cr, uid, [('created_feature','=',False),('id','=',ids[0])])
        if search_ids:
            self_data = self.browse(cr, uid, search_ids[0])
            phone = self_data.dsr_phone_no
            sim = self_data.dsr_sim_no
            imei = self_data.dsr_imei_no
            if self_data.dsr_talk_n_text:
                intl_code = self_data.dsr_talk_soc.id
                if not intl_code:
                    intl_code = prod_obj.search(cr, uid, [('dsr_categ_id','=','prepaid'),('is_intl','=',True)])[0]
                search_intl_ids = self.search(cr, uid, [('dsr_product_description','=',intl_code),('created_feature','=',True),('prepaid_id','=',ids[0])])
                if search_intl_ids:
                    self.unlink(cr, uid, search_intl_ids)
            if self_data.dsr_tether:
                tether_code = self_data.dsr_tether_soc.id
                if not tether_code:
                    tether_code = prod_obj.search(cr, uid, [('dsr_categ_id','=','prepaid'),('is_tether','=',True)])[0]
                search_tether_ids = self.search(cr, uid, [('dsr_product_description','=',tether_code),('created_feature','=',True),('prepaid_id','=',ids[0])])
                if search_tether_ids:
                    self.unlink(cr, uid, search_tether_ids)
            if self_data.dsr_php:
                php_code = self_data.dsr_php_soc.id
                if not php_code:
                    php_code = prod_obj.search(cr, uid, [('dsr_categ_id','=','prepaid'),('is_php','=',True)])[0]
                search_php_ids = self.search(cr, uid, [('dsr_product_description','=',php_code),('created_feature','=',True),('prepaid_id','=',ids[0])])
                if search_php_ids:
                    self.unlink(cr, uid, search_php_ids)
            if self_data.dsr_score:
                score_code = self_data.dsr_score_soc.id
                if not score_code:
                    score_code = prod_obj.search(cr, uid, [('dsr_categ_id','=','prepaid'),('is_score','=',True)])[0]
                search_score_ids = self.search(cr, uid, [('dsr_product_description','=',score_code),('created_feature','=',True),('prepaid_id','=',ids[0])])
                if search_score_ids:
                    self.unlink(cr, uid, search_score_ids)
        res = super(wireless_dsr_prepaid_line, self).unlink(cr, uid, ids, context=context)
        return res

wireless_dsr_prepaid_line()

############## Feature Line One2Many ###############################
class wireless_dsr_feature_line(osv.osv):
    _name = 'wireless.dsr.feature.line'
    _description = "Wireless DSR Feature Line"
    _order = 'id desc'

    def _calculate_rev(self, cr, uid, revenue_id, product, interval_type, phone_purchase, line_no, spiff_no_consider):
        val = {}
        tac_master_ids = []
        is_commission = True
        is_spiff = True
        is_added = True
        is_bonus_comm = True
        is_bonus_spiff = True
        revenue_obj = self.pool.get('revenue.generate.master')
        product_obj = self.pool.get('product.product')
        tac_obj = self.pool.get('tac.code.master')
        mul_factor = revenue_obj.browse(cr, uid, revenue_id).dsr_revenue_calc
        exclude_scnc = revenue_obj.browse(cr, uid, revenue_id).exclude_scnc
        spiff_factor = revenue_obj.browse(cr, uid, revenue_id).dsr_phone_spiff
        added_rev = revenue_obj.browse(cr, uid, revenue_id).dsr_added_rev
        bonus_line_spiff = revenue_obj.browse(cr, uid, revenue_id).bonus_line_spiff
        bonus_handset_spiff = revenue_obj.browse(cr, uid, revenue_id).bonus_handset_spiff
        month_acc = product_obj.browse(cr, uid, product).monthly_access
        is_scnc  = product_obj.browse(cr, uid, product).is_scnc
        val = {
                'comm':0.00,
                'spiff':0.00,
                'added':0.00,
                'tot':0.00
            }
        if not line_no:
            line_no = 0
        cr.execute("select eligible_commission,eligible_spiff,eligible_added,eligible_bonus_comm,eligible_bonus_spiff from transaction_line_soc_rel where line_no = %s and (soc_code=%s or sub_soc_code=%s)"%(line_no,product,product))
        cal_data = cr.fetchall()
        for cal_data_each in cal_data:
            if cal_data_each:
                is_commission = cal_data_each[0]
                is_spiff = cal_data_each[1]
                is_added = cal_data_each[2]
                is_bonus_comm = cal_data_each[3]
                is_bonus_spiff = cal_data_each[4]
        # if tac_ids and imei:
        #     for tac_id in tac_ids:
        #         if tac_id:
        #             tac_master_ids.append(tac_id[0])
        # if tac_master_ids and imei:
        #     for tac_data in tac_obj.browse(cr, uid, tac_master_ids):
        #         if imei[:8] == tac_data.tac_code:
        #             spiff_no_consider = True
        if is_bonus_comm:
            val['comm'] = (mul_factor * month_acc) + bonus_line_spiff
        else:
            val['comm'] = (mul_factor * month_acc)
        val['added'] = added_rev
        if is_bonus_spiff:
            val['spiff'] = (spiff_factor * month_acc) + bonus_handset_spiff
        else:
            val['spiff'] = (spiff_factor * month_acc)
        if interval_type == 'at_act':
            if exclude_scnc == True:
                if is_scnc == False:
                    if phone_purchase != 'sim_only':
                        if spiff_no_consider:
                            if is_commission:
                                val['tot'] = val['comm']
                            else:
                                vals['comm'] = 0
                            if is_added:
                                val['tot'] = val['tot'] + val['added']
                            else:
                                val['added'] = 0
                            val['spiff'] = 0
                        else:
                            if is_commission:
                                val['tot'] = val['comm']
                            else:
                                val['comm'] = 0
                            if is_added:
                                val['tot'] = val['tot'] + val['added']
                            else:
                                val['added'] = 0
                            if is_spiff:
                                val['tot'] = val['tot'] + val['spiff']
                            else:
                                val['spiff'] = 0
                        return val
                    else:
                        if is_commission:
                            val['tot'] = val['comm']
                        else:
                            val['comm'] = 0
                        if is_added:
                            val['tot'] = val['tot'] + val['added']
                        else:
                            val['added'] = 0
                        val['spiff'] = 0.00
                        return val
                else:
                    if phone_purchase != 'sim_only':
                        if spiff_no_consider:
                            if is_commission:
                                val['tot'] = val['comm']
                            else:
                                val['comm'] = 0
                            val['spiff'] = 0
                        else:
                            if is_commission:
                                val['tot'] = val['comm']
                            else:
                                val['comm'] = 0
                            if is_spiff:
                                val['tot'] = val['tot'] + val['spiff']
                            else:
                                val['spiff'] = 0
                        val['added'] = 0.00
                        return val
                    else:
                        if is_commission:
                            val['tot'] = val['comm']
                        else:
                            val['comm'] = 0
                        val['added'] = 0.00
                        val['spiff'] = 0.00
                        return val
            else:
                if phone_purchase != 'sim_only':
                    if spiff_no_consider:
                        if is_commission:
                            val['tot'] = val['comm']
                        else:
                            val['comm'] = 0
                        if is_added:
                            val['tot'] = val['tot'] + val['added']
                        else:
                            val['added'] = 0
                        val['spiff'] = 0
                    else:
                        if is_commission:
                            val['tot'] = val['comm']
                        else:
                            val['comm'] = 0
                        if is_spiff:
                            val['tot'] = val['tot'] + val['spiff']
                        else:
                            val['spiff'] = 0
                        if is_added:
                            val['tot'] = val['tot'] + val['added']
                        else:
                            val['added'] = 0
                    return val
                else:
                    if is_commission:
                        val['tot'] = val['comm']
                    else:
                        val['comm'] = 0
                    if is_added:
                        val['tot'] = val['tot'] + val['added']
                    else:
                        val['added'] = 0
                    val['spiff'] = 0.00
                    return val
        else:
            if phone_purchase != 'sim_only':
                if spiff_no_consider:
                    if is_commission:
                        val['tot'] = val['comm']
                    else:
                        val['comm'] = 0
                    if is_added:
                        val['tot'] = val['tot'] + val['added']
                    else:
                        val['added'] = 0
                    val['spiff'] = 0
                else:
                    if is_commission:
                        val['tot'] = val['comm']
                    else:
                        val['comm'] = 0
                    if is_spiff:
                        val['tot'] = val['tot'] + val['spiff']
                    else:
                        val['spiff'] = 0
                    if is_added:
                        val['tot'] = val['tot'] + val['added']
                    else:
                        val['added'] = 0
                return val
            else:
                if is_commission:
                    val['tot'] = val['comm']
                else:
                    val['comm'] = 0
                if is_added:
                    val['tot'] = val['tot'] + val['added']
                else:
                    val['added'] = 0
                val['spiff'] = 0.00
                return val

#################### Changed due to Odoo 8 new functionality ###################################
    def _calculate_feature_rev_wrapper(self, cr, uid, ids, field_name, arg, context=None):
        x = self._calculate_feature_revenue(cr, uid, ids, field_name, arg, context=context)
        return x

    def _calculate_feature_revenue(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        tac_record_ids = []
        phone_purchase = ''
        spiff_no_consider = False
        line = self.browse(cr, uid, ids[0], context=context)
        revenue_obj = self.pool.get('revenue.generate.master')
        product_obj = self.pool.get('product.product')
        tac_obj = self.pool.get('tac.code.master')
        res[line.id] = {
                'dsr_rev_gen': 0.00,
                'dsr_comm_amnt':0.00,
                'dsr_comm_spiff':0.00,
                'dsr_comm_added':0.00,
                'dsr_comm_per_line':0.00
            }
        product_type = line.dsr_product_type.id
        prod_type_name = line.dsr_product_type.name
        interval_type = line.dsr_activiation_interval
        if line.postpaid_id.id:
            phone_purchase = line.postpaid_id.dsr_phone_purchase_type
        credit_class_type = False
        if line.dsr_credit_class:
            credit_class_type = line.dsr_credit_class.category_type.id
        product = line.dsr_product_code.id
        line_no = line.dsr_line_no.id
        dsr_jod = False
        imei = line.dsr_imei_no
        if imei:
            tac_record_ids = tac_obj.search(cr, uid, [('tac_code','=',imei[:8])])
        prod_code_type = self.pool.get('product.product').browse(cr, uid, product).dsr_prod_code_type.id
        dsr_id = line.feature_product_id.id
        dsr_data = self.pool.get('wireless.dsr').browse(cr, uid, dsr_id)
        trans_date = dsr_data.dsr_date
        emp_des = dsr_data.dsr_designation_id.id
        comm_percent = 0.00
        base_comm_obj = self.pool.get('comm.basic.commission.formula')
        base_comm_search = base_comm_obj.search(cr, uid, [('comm_designation','=',emp_des),('comm_start_date','<=',trans_date),('comm_end_date','>=',trans_date),('comm_inactive','=',False)])
        if base_comm_search:
            comm_percent = base_comm_obj.browse(cr, uid, base_comm_search[0]).comm_percent
        else:
            base_comm_search = base_comm_obj.search(cr, uid, [('comm_start_date','<=',trans_date),('comm_end_date','>=',trans_date),('comm_inactive','=',False)])
            if base_comm_search:
                comm_percent = base_comm_obj.browse(cr, uid, base_comm_search[0]).comm_percent
        rev_root_ids = revenue_obj.search(cr, uid, [('dsr_prod_type','=',product_type),('dsr_start_date','<=',trans_date),('dsr_end_date','>=',trans_date),('inactive','=',False)])
        if rev_root_ids:
            where_condition = []
            where_condition.append(('id','in',rev_root_ids))
            compare_string = str("")
            if len(rev_root_ids) == 1:
                compare_string += str("= %s"%(rev_root_ids[0]))
            else:
                compare_string += str("in %s"%(tuple(rev_root_ids),))
            cr.execute("select distinct(dsr_activation_type) from revenue_generate_master where id "+compare_string+"")
            master_interval_type = map(lambda x: x[0], cr.fetchall())
            cr.execute("select distinct(dsr_prod_code_type) from revenue_generate_master where id "+compare_string+"")
            master_prod_code_type = map(lambda x: x[0], cr.fetchall())
            cr.execute("select distinct(dsr_rev_product) from revenue_generate_master where id "+compare_string+"")
            master_product_ids = map(lambda x: x[0], cr.fetchall())
            cr.execute("select distinct(dsr_credit_class_type) from revenue_generate_master where id "+compare_string+"")
            master_class_type = map(lambda x: x[0], cr.fetchall())
            if interval_type in master_interval_type:
                where_condition.append(('dsr_activation_type','=',interval_type))
            if prod_code_type in master_prod_code_type:
                where_condition.append(('dsr_prod_code_type','=',prod_code_type))
            if credit_class_type in master_class_type:
                where_condition.append(('dsr_credit_class_type','=',credit_class_type))
            if product in master_product_ids:
                where_condition.append(('dsr_rev_product','=',product))
            
            rev_final_ids = revenue_obj.search(cr, uid, where_condition)
            if rev_final_ids:
                compare_string = str("")
                if len(rev_final_ids) == 1:
                    compare_string += str("= %s"%(rev_final_ids[0]))
                else:
                    compare_string += str("in %s"%(tuple(rev_final_ids),))
                if tac_record_ids:
                    cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                            where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = false or rev.is_exclude is null)
                            and rev.dsr_jod = %s and tc.tac_id = %s''',(dsr_jod,tac_record_ids[0]))
                    revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                    if revenue_master_ids:
                        tac_ids = []
                        val = self._calculate_rev(cr, uid, revenue_master_ids[0], product, interval_type, phone_purchase, line_no, spiff_no_consider)
                        res[line.id]['dsr_rev_gen'] = val['tot']
                        res[line.id]['dsr_comm_per_line'] = float(res[line.id]['dsr_rev_gen'] * comm_percent / 100)
                        res[line.id]['dsr_comm_amnt'] = val['comm']
                        res[line.id]['dsr_comm_spiff'] = val['spiff']
                        res[line.id]['dsr_comm_added'] = val['added']
                        return res
                cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                        where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = true or rev.is_exclude is null)
                        and rev.dsr_jod = %s''',(dsr_jod,))
                revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                if revenue_master_ids:
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(revenue_master_ids[0]))
                    tac_ids = map(lambda x: x[0], cr.fetchall())
                    for tac_record_each in tac_record_ids:
                        if tac_record_each in tac_ids:
                            spiff_no_consider = True
                    val = self._calculate_rev(cr, uid, revenue_master_ids[0], product, interval_type, phone_purchase, line_no, spiff_no_consider)
                    res[line.id]['dsr_rev_gen'] = val['tot']
                    res[line.id]['dsr_comm_per_line'] = float(res[line.id]['dsr_rev_gen'] * comm_percent / 100)
                    res[line.id]['dsr_comm_amnt'] = val['comm']
                    res[line.id]['dsr_comm_spiff'] = val['spiff']
                    res[line.id]['dsr_comm_added'] = val['added']
                    return res
                cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                        where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = true or rev.is_exclude is null)
                        and (rev.dsr_jod is null or rev.dsr_jod = false)''')
                revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                if revenue_master_ids:
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(revenue_master_ids[0]))
                    tac_ids = map(lambda x: x[0], cr.fetchall())
                    for tac_record_each in tac_record_ids:
                        if tac_record_each in tac_ids:
                            spiff_no_consider = True
                    val = self._calculate_rev(cr, uid, revenue_master_ids[0], product, interval_type, phone_purchase, line_no, spiff_no_consider)
                    res[line.id]['dsr_rev_gen'] = val['tot']
                    res[line.id]['dsr_comm_per_line'] = float(res[line.id]['dsr_rev_gen'] * comm_percent / 100)
                    res[line.id]['dsr_comm_amnt'] = val['comm']
                    res[line.id]['dsr_comm_spiff'] = val['spiff']
                    res[line.id]['dsr_comm_added'] = val['added']
                    return res
                cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                        where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = false or rev.is_exclude is null)
                        and (rev.dsr_jod is null or rev.dsr_jod = false)''')
                revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                if revenue_master_ids:
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(revenue_master_ids[0]))
                    tac_ids = map(lambda x: x[0], cr.fetchall())
                    for tac_record_each in tac_record_ids:
                        if tac_record_each not in tac_ids:
                            spiff_no_consider = True
                    val = self._calculate_rev(cr, uid, revenue_master_ids[0], product, interval_type, phone_purchase, line_no, spiff_no_consider)
                    res[line.id]['dsr_rev_gen'] = val['tot']
                    res[line.id]['dsr_comm_per_line'] = float(res[line.id]['dsr_rev_gen'] * comm_percent / 100)
                    res[line.id]['dsr_comm_amnt'] = val['comm']
                    res[line.id]['dsr_comm_spiff'] = val['spiff']
                    res[line.id]['dsr_comm_added'] = val['added']
                    return res
            revenue_base_ids = revenue_obj.search(cr, uid, [('id','in',rev_final_ids),('is_exclude','=',False),('exclude_tac_code','=',False),('dsr_jod','=',False)])
            if revenue_base_ids:
                tac_ids = []
                val = self._calculate_rev(cr, uid, revenue_base_ids[0], product, interval_type, phone_purchase, line_no, spiff_no_consider)
                res[line.id]['dsr_rev_gen'] = val['tot']
                res[line.id]['dsr_comm_per_line'] = float(res[line.id]['dsr_rev_gen'] * comm_percent / 100)
                res[line.id]['dsr_comm_amnt'] = val['comm']
                res[line.id]['dsr_comm_spiff'] = val['spiff']
                res[line.id]['dsr_comm_added'] = val['added']
                return res
        res[line.id]['dsr_rev_gen'] = 0
        res[line.id]['dsr_comm_per_line'] = 0
        res[line.id]['dsr_comm_amnt'] = 0
        res[line.id]['dsr_comm_spiff'] = 0
        res[line.id]['dsr_comm_added'] = 0
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('wireless.dsr.feature.line').browse(cr, uid, ids, context=context):
            result[line.id] = True
        return result.keys()

    _columns = {
                'feature_product_id':fields.many2one('wireless.dsr','Product Id'),
                'dsr_trans_type':fields.selection(_prod_type, 'Transaction Type'),
                # 'creation_date':fields.date('Creation Date'),
                'dsr_product_type':fields.many2one('product.category','Product Type'),
                # 'dsr_product_code_type':fields.char('Product Code Type', size=64),
                ### below product Code type added for testing benefit
                'dsr_product_code_type':fields.many2one('product.category','Product Code Type'),

                'dsr_product_code':fields.many2one('product.product', 'Product Code'),                
                # 'dsr_product_description':fields.char('Product Description', size=64),
                'act_type':fields.selection([('Act','Activation'),('reactivation','Reactivation'),('deactivation','DeActivation')], 'Activation Type'),
                'is_jump':fields.boolean('JUMP'),
                'dsr_credit_class':fields.many2one('credit.class', 'Credit class'),
                # 'dsr_credit_class_type':fields.many2one('credit.class.type', 'Credit Class Type'),
                'dsr_activiation_interval':fields.selection([('at_act','At Time of Activation'),('after_act','After Activation')],'Activation Interval'),
                'dsr_phone_no':fields.char('Mobile Phone', size=10),
                'dsr_emp_type':fields.many2one('dsr.employee.type','T-Mobile Employee'),
                'is_emp_upg':fields.boolean('Employee Upgrade'),
                'dsr_p_number':fields.char('P-number'),
                'dsr_line_no':fields.many2one('credit.line.limit','Line #'),
                'dsr_cust_ban_no':fields.char('BAN #', size=16),
                'dsr_sim_no': fields.char('SIM #', size=25),
                'dsr_imei_no':fields.char('IMEI #', size=15),
                'dsr_jump':fields.boolean('JUMP already on account'),
                'dsr_eip_no':fields.char('EIP #', size=16),
                'dsr_warranty':fields.char('Warranty Exchange Order #', size=16),
                'dsr_act_date':fields.date('Activation Date'),
                'pseudo_date':fields.date('Pseudo Transaction Date'),
                'dsr_deact_date':fields.date('DeActivation Date'),
                'act_recon':fields.boolean('Act Date Reconciled'),
                'deact_recon':fields.boolean('DeAct Reconciled'),
                'dsr_react_date':fields.date('ReActivation Date'),
                'react_recon':fields.boolean('ReAct Reconciled'),
                'dsr_rev_gen':fields.function(_calculate_feature_rev_wrapper, string="Total Rev Gen.", type='float', multi='sums',
                        store={
                                'wireless.dsr.feature.line': (_get_order, [], 10),
                }),
                'dsr_comm_amnt':fields.function(_calculate_feature_rev_wrapper, string="DSR Commission Amount", type='float', multi='sums',
                        store={
                                'wireless.dsr.feature.line': (_get_order, [], 10),
                }),
                'dsr_comm_spiff':fields.function(_calculate_feature_rev_wrapper, string="DSR Spiff Amount", type='float', multi='sums',
                        store={
                                'wireless.dsr.feature.line': (_get_order, [], 10),
                }),
                'dsr_comm_added':fields.function(_calculate_feature_rev_wrapper, string="DSR Added Amount", type='float', multi='sums',
                        store={
                                'wireless.dsr.feature.line': (_get_order, [], 10),
                }),
                'dsr_comm_per_line':fields.function(_calculate_feature_rev_wrapper, string="Commission per line", type='float', multi='sums',
                    store={
                                'wireless.dsr.feature.line': (_get_order, [], 10),
                }),
                'created_upgrade':fields.boolean('Created From Upgrade'),
                'dsr_phone_purchase_type':fields.selection([('new_device','EIP'),('device_outright','Device Outright'),('sim_only','No Purchase')],'Phone Purchase'),
                'postpaid_id':fields.many2one('wireless.dsr.postpaid.line', 'Postpaid ID'),
                'upgrade_id':fields.many2one('wireless.dsr.upgrade.line', 'Upgrade ID'),
                'dsr_smd':fields.boolean('SMD'),
                'valid': fields.many2one('crashing.validation.flag','Valid'),
                'dsr_trade_inn':fields.selection([('yes','Yes'),('no','No')],'Trade-in'),
                'dsr_contract_term':fields.integer('Contract Term'),
                'dsr_temp_no':fields.char('Temporary #', size=10),
                'dsr_monthly_access':fields.float('Monthle Access'),
                'dsr_pmd': fields.boolean('PMD'),
                'comments': fields.text('Reasons For Deactivation of Chargebacks'),
                'noncommissionable':fields.boolean('Non Commissionable'),
                'spiff_amt': fields.float('Spiff Amt'),
                'commission_amt': fields.float('Commissions Amt'),
                'crash_act_date': fields.date('Crashing Activation Date'),
                'crash_deact_date': fields.date('Crashing Deactivation Date'),
                'crash_react_date': fields.date('Crashing Reactivation Date'),
                'dsr_jod':fields.boolean('JUMP on Demand'),
                # 'dsr_crash_activation': fields.many2one('dsr.tmob.crash.process','Activation'),
                # 'dsr_crash_deactivation': fields.many2one('dsr.crash.process.deactivation','Deactivation'),
                'employee_id' : fields.many2one('hr.employee','Emp'),
                'store_id':fields.many2one('sap.store', 'Store'),
                'market_id':fields.many2one('market.place', 'Market'),
                'region_id':fields.many2one('market.regions', 'Region'),
                'eip_phone_purchase':fields.boolean('EIP Phone Purchased'),
                'dsr_jump_already':fields.boolean('JUMP already on Account'),
                'dsr_phone_first':fields.many2one('phone.type.master', 'Device Type'),
                'dsr_transaction_id':fields.char('Transaction ID', size=64),
                'state':fields.selection([('draft','Draft'),('pending','Pending'),('cancel','Cancel'),('done','Done'),('void','VOID')],'State', readonly=True),
                'customer_name':fields.char('Customer Name', size=1024),
                'dealer_code':fields.char('Dealer Code', size=1024),
                'dsr_mob_port':fields.boolean('Mobile Port'),
                'dsr_port_comp':fields.many2one('port.company', 'Port Company'),
                'dsr_ship_to':fields.boolean('Ship To'),
                'dsr_exception':fields.boolean('Exception'),
                'dsr_designation_id':fields.many2one('hr.job','Designation')
		#'tmob_comments' : fields.text('Tmobile Comments'),#### field added as per the change to update the T-mobile comments
		#'valid_neutral': fields.many2one('crashing.validation.flag','Valid Non-Zero'),#### field added to be used for nonzero crash
    }
    _defaults = {
                'act_type':'Act',
                'state':'draft',
                'dsr_activiation_interval':'after_act',
                'dsr_trans_type':'feature',
                'created_upgrade':False,
                'dsr_exception':False,
                'dsr_jod':False
    }

    def onchange_emp_type(self, cr, uid, ids, dsr_emp_type):
        emp_obj = self.pool.get('dsr.employee.type')
        is_emp_upg = False
        if dsr_emp_type:
            emp_data = emp_obj.browse(cr, uid, dsr_emp_type)
            if emp_data.is_emp_upg:
                is_emp_upg = True
            return {'value':{'is_emp_upg':is_emp_upg,'dsr_p_number':False}}
        return {'value':{'is_emp_upg':is_emp_upg,'dsr_p_number':False}}

    def onchange_soc(self, cr, uid, ids, product):
        prod_obj = self.pool.get('product.product')
        if product:
            prod_data = prod_obj.browse(cr, uid, product)
            prod_code_type = prod_data.dsr_prod_code_type.id
            monthly_access = prod_data.monthly_access
            contract_term = prod_data.contract_term
            if (prod_data.is_php == True) or (prod_data.is_jump == True):
                is_jump = True
                return {'value': {'is_jump' : True,
                                'dsr_product_code_type':prod_code_type,
                                'dsr_monthly_access':monthly_access,
                                'dsr_contract_term':contract_term}}
            else:
                return {'value': {'is_jump':False,
                                'dsr_product_code_type':prod_code_type,
                                'dsr_monthly_access':monthly_access,
                                'dsr_contract_term':contract_term}}
        return {'value':{'is_jump':False,
                        'dsr_product_code_type':False,
                        'dsr_monthly_access':False,
                        'dsr_contract_term':False
                }}

    def onchange_product_type(self, cr, uid, ids, product_type):
        if product_type:
            return {'value': {'dsr_product_code' : False}}
        return {}

    def onchange_phone(self, cr, uid, ids, phone):
        if phone:
            phone_check(phone)
            return {}
        return {}

    def onchange_sim(self, cr, uid, ids, sim):
        if sim:
            sim_validation(sim)
            return {}
        return {}

    # def onchange_imei(self, cr, uid, ids, imei):
    #     if imei:
    #         imei_check(imei)
    #         return {}
    #     return {}

    # def onchange_credit_class(self, cr, uid, ids, dsr_credit_class):
    #     cc_obj = self.pool.get('credit.class')
    #     if dsr_credit_class:
    #         cc_data = cc_obj.browse(cr, uid, dsr_credit_class)
    #         cc_type = cc_data.category_type.id
    #         return {'value':{'dsr_credit_class_type':cc_type}}
    #     return {}

    def create(self, cr, uid, vals, context=None):
        prod_type = False
        if 'dsr_product_type' in vals:
            prod_type = vals['dsr_product_type']
        if 'dsr_phone_no' in vals:
            phone = vals['dsr_phone_no']
            phone_check(phone)
        # if 'dsr_imei_no' in vals:
        #     number = vals['dsr_imei_no']
        #     imei_check(number)
        if 'dsr_sim_no' in vals:
            card_number = vals['dsr_sim_no']
            sim_validation(card_number)
        res = super(wireless_dsr_feature_line, self).create(cr, uid, vals, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        prod_type = False
        if 'dsr_product_type' in vals:
            prod_type = vals['dsr_product_type']
        if 'dsr_phone_no' in vals:
            phone = vals['dsr_phone_no']
            phone_check(phone)
        # if 'dsr_imei_no' in vals:
        #     number = vals['dsr_imei_no']
        #     imei_check(number)
        if 'dsr_sim_no' in vals:
            card_number = vals['dsr_sim_no']
            sim_validation(card_number)
        res = super(wireless_dsr_feature_line, self).write(cr, uid, ids, vals, context=context)
        return res
        
wireless_dsr_feature_line()

############# Upgrade DSR Entry One2Many ##############################
class wireless_dsr_upgrade_line(osv.osv):
    _name = 'wireless.dsr.upgrade.line'
    _description = "Wireless DSR Upgrade Line"
    _order = 'id desc'

    def _calculate_rev(self, cr, uid, revenue_id, phone_purchase, product, line_no, spiff_no_consider):
        val = {}
        tac_master_ids = []
        is_commission = True
        is_spiff = True
        is_added = True
        is_bonus_comm = True
        is_bonus_spiff = True
        revenue_obj = self.pool.get('revenue.generate.master')
        product_obj = self.pool.get('product.product')
        tac_obj = self.pool.get('tac.code.master')
        mul_factor = revenue_obj.browse(cr, uid, revenue_id).dsr_revenue_calc
        spiff_factor = revenue_obj.browse(cr, uid, revenue_id).dsr_phone_spiff
        added_rev = revenue_obj.browse(cr, uid, revenue_id).dsr_added_rev
        bonus_line_spiff = revenue_obj.browse(cr, uid, revenue_id).bonus_line_spiff
        bonus_handset_spiff = revenue_obj.browse(cr, uid, revenue_id).bonus_handset_spiff
        month_acc = product_obj.browse(cr, uid, product).monthly_access
        val = {
                'comm':0.00,
                'spiff':0.00,
                'added':0.00,
                'tot':0.00
        }
        if not line_no:
            line_no = 0
        cr.execute("select eligible_commission,eligible_spiff,eligible_added,eligible_bonus_comm,eligible_bonus_spiff from transaction_line_soc_rel where line_no = %s and (soc_code=%s or sub_soc_code=%s)"%(line_no,product,product))
        cal_data = cr.fetchall()
        for cal_data_each in cal_data:
            if cal_data_each:
                is_commission = cal_data_each[0]
                is_spiff = cal_data_each[1]
                is_added = cal_data_each[2]
                is_bonus_comm = cal_data_each[3]
                is_bonus_spiff = cal_data_each[4]
        # if tac_ids and imei:
        #     for tac_id in tac_ids:
        #         if tac_id:
        #             tac_master_ids.append(tac_id[0])
        # if tac_master_ids and imei:
        #     for tac_data in tac_obj.browse(cr, uid, tac_master_ids):
        #         if imei[:8] == tac_data.tac_code:
        #             spiff_no_consider = True
        if is_bonus_comm:
            val['comm'] = (mul_factor * month_acc) + bonus_line_spiff
        else:
            val['comm'] = (mul_factor * month_acc)
        val['added'] = added_rev
        if is_bonus_spiff:
            val['spiff'] = (spiff_factor * month_acc) + bonus_handset_spiff
        else:
            val['spiff'] = (spiff_factor * month_acc)
        if spiff_no_consider:
            if is_commission:
                val['tot'] = val['comm']
            else:
                val['comm'] = 0
            if is_added:
                val['tot'] = val['tot'] + val['added']
            else:
                val['added'] = 0
            val['spiff'] = 0
        else:
            if is_commission:
                val['tot'] = val['comm']
            else:
                val['comm'] = 0
            if is_spiff:
                val['tot'] = val['tot'] + val['spiff']
            else:
                val['spiff'] = 0
            if is_added:
                val['tot'] = val['tot'] + val['added']
            else:
                val['added'] = 0
        return val

    def _calculate_upgrade_revenue(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        tac_record_ids = []
        spiff_no_consider= False
        line = self.browse(cr, uid, ids[0], context=context)
        revenue_obj = self.pool.get('revenue.generate.master')
        product_obj = self.pool.get('product.product')
        tac_obj = self.pool.get('tac.code.master')
        res[line.id] = {
                'dsr_rev_gen': 0.00,
                'dsr_comm_amnt':0.00,
                'dsr_comm_added':0.00,
                'dsr_comm_spiff':0.00,
                'dsr_comm_per_line':0.00
            }
        product_type = line.dsr_product_type.id
        # credit_class_type = line.dsr_credit_class.category_type.id
        credit_class_type = False
        product = line.dsr_product_code.id
        prod_code_type = self.pool.get('product.product').browse(cr, uid, product).dsr_prod_code_type.id
        phone_purchase = line.dsr_phone_purchase_type
        dsr_id = line.product_id.id
        line_no = line.dsr_line_no.id
        dsr_jod = line.dsr_jod
        imei = line.dsr_imei_no
        if imei:
            tac_record_ids = tac_obj.search(cr, uid, [('tac_code','=',imei[:8])])
        dsr_data = self.pool.get('wireless.dsr').browse(cr, uid, dsr_id)
        trans_date = dsr_data.dsr_date
        emp_des = dsr_data.dsr_designation_id.id
        comm_percent = 0.00
        base_comm_obj = self.pool.get('comm.basic.commission.formula')
        base_comm_search = base_comm_obj.search(cr, uid, [('comm_designation','=',emp_des),('comm_start_date','<=',trans_date),('comm_end_date','>=',trans_date),('comm_inactive','=',False)])
        if base_comm_search:
            comm_percent = base_comm_obj.browse(cr, uid, base_comm_search[0]).comm_percent
        else:
            base_comm_search = base_comm_obj.search(cr, uid, [('comm_start_date','<=',trans_date),('comm_end_date','>=',trans_date),('comm_inactive','=',False)])
            if base_comm_search:
                comm_percent = base_comm_obj.browse(cr, uid, base_comm_search[0]).comm_percent
        rev_root_ids = revenue_obj.search(cr, uid, [('dsr_prod_type','=',product_type),('dsr_start_date','<=',trans_date),('dsr_end_date','>=',trans_date),('inactive','=',False)])
        comm_percent = 10.00
        if rev_root_ids:
            where_condition = []
            where_condition.append(('id','in',rev_root_ids))
            compare_string = str("")
            if len(rev_root_ids) == 1:
                compare_string += str("= %s"%(rev_root_ids[0]))
            else:
                compare_string += str("in %s"%(tuple(rev_root_ids),))
            cr.execute("select distinct(dsr_prod_code_type) from revenue_generate_master where id "+compare_string+"")
            master_prod_code_type = map(lambda x: x[0], cr.fetchall())
            cr.execute("select distinct(dsr_rev_product) from revenue_generate_master where id "+compare_string+"")
            master_product_ids = map(lambda x: x[0], cr.fetchall())
            cr.execute("select distinct(dsr_credit_class_type) from revenue_generate_master where id "+compare_string+"")
            master_class_type = map(lambda x: x[0], cr.fetchall())
            
            if prod_code_type in master_prod_code_type:
                where_condition.append(('dsr_prod_code_type','=',prod_code_type))
            if credit_class_type in master_class_type:
                where_condition.append(('dsr_credit_class_type','=',credit_class_type))
            if product in master_product_ids:
                where_condition.append(('dsr_rev_product','=',product))
            
            rev_final_ids = revenue_obj.search(cr, uid, where_condition)
            if rev_final_ids:
                compare_string = str("")
                if len(rev_final_ids) == 1:
                    compare_string += str("= %s"%(rev_final_ids[0]))
                else:
                    compare_string += str("in %s"%(tuple(rev_final_ids),))
                if tac_record_ids:
                    cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                            where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = false or rev.is_exclude is null)
                            and rev.dsr_jod = %s and tc.tac_id = %s''',(dsr_jod,tac_record_ids[0]))
                    revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                    if revenue_master_ids:
                        tac_ids = []
                        val = self._calculate_rev(cr, uid, revenue_master_ids[0], phone_purchase, product, line_no, spiff_no_consider)
                        res[line.id]['dsr_rev_gen'] = val['tot']
                        res[line.id]['dsr_comm_per_line'] = float(res[line.id]['dsr_rev_gen'] * comm_percent / 100)
                        res[line.id]['dsr_comm_amnt'] = val['comm']
                        res[line.id]['dsr_comm_added'] = val['added']
                        res[line.id]['dsr_comm_spiff'] = val['spiff']
                        return res
                cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                        where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = true or rev.is_exclude is null)
                        and rev.dsr_jod = %s''',(dsr_jod,))
                revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                if revenue_master_ids:
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(revenue_master_ids[0]))
                    tac_ids = map(lambda x: x[0], cr.fetchall())
                    for tac_record_each in tac_record_ids:
                        if tac_record_each in tac_ids:
                            spiff_no_consider = True
                    val = self._calculate_rev(cr, uid, revenue_master_ids[0], phone_purchase, product, line_no, spiff_no_consider)
                    res[line.id]['dsr_rev_gen'] = val['tot']
                    res[line.id]['dsr_comm_per_line'] = float(res[line.id]['dsr_rev_gen'] * comm_percent / 100)
                    res[line.id]['dsr_comm_amnt'] = val['comm']
                    res[line.id]['dsr_comm_added'] = val['added']
                    res[line.id]['dsr_comm_spiff'] = val['spiff']
                    return res
                cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                        where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = true or rev.is_exclude is null)
                        and (rev.dsr_jod is null or rev.dsr_jod = false)''')
                revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                if revenue_master_ids:
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(revenue_master_ids[0]))
                    tac_ids = map(lambda x: x[0], cr.fetchall())
                    for tac_record_each in tac_record_ids:
                        if tac_record_each in tac_ids:
                            spiff_no_consider = True
                    val = self._calculate_rev(cr, uid, revenue_master_ids[0], phone_purchase, product, line_no, spiff_no_consider)
                    res[line.id]['dsr_rev_gen'] = val['tot']
                    res[line.id]['dsr_comm_per_line'] = float(res[line.id]['dsr_rev_gen'] * comm_percent / 100)
                    res[line.id]['dsr_comm_amnt'] = val['comm']
                    res[line.id]['dsr_comm_added'] = val['added']
                    res[line.id]['dsr_comm_spiff'] = val['spiff']
                    return res
                cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                        where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = false or rev.is_exclude is null)
                        and (rev.dsr_jod is null or rev.dsr_jod = false)''')
                revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                if revenue_master_ids:
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(revenue_master_ids[0]))
                    tac_ids = map(lambda x: x[0], cr.fetchall())
                    for tac_record_each in tac_record_ids:
                        if tac_record_each not in tac_ids:
                            spiff_no_consider = True
                    val = self._calculate_rev(cr, uid, revenue_master_ids[0], phone_purchase, product, line_no, spiff_no_consider)
                    res[line.id]['dsr_rev_gen'] = val['tot']
                    res[line.id]['dsr_comm_per_line'] = float(res[line.id]['dsr_rev_gen'] * comm_percent / 100)
                    res[line.id]['dsr_comm_amnt'] = val['comm']
                    res[line.id]['dsr_comm_added'] = val['added']
                    res[line.id]['dsr_comm_spiff'] = val['spiff']
                    return res
            revenue_base_ids = revenue_obj.search(cr, uid, [('id','in',rev_final_ids),('is_exclude','=',False),('exclude_tac_code','=',False),('dsr_jod','=',False)])
            if revenue_base_ids:
                tac_ids = []
                val = self._calculate_rev(cr, uid, revenue_base_ids[0], phone_purchase, product, line_no, spiff_no_consider)
                res[line.id]['dsr_rev_gen'] = val['tot']
                res[line.id]['dsr_comm_per_line'] = float(res[line.id]['dsr_rev_gen'] * comm_percent / 100)
                res[line.id]['dsr_comm_amnt'] = val['comm']
                res[line.id]['dsr_comm_added'] = val['added']
                res[line.id]['dsr_comm_spiff'] = val['spiff']
                return res
        res[line.id]['dsr_rev_gen'] = 0.00
        res[line.id]['dsr_comm_per_line'] = 0.00
        res[line.id]['dsr_comm_amnt'] = 0.00
        res[line.id]['dsr_comm_spiff'] = 0.00
        res[line.id]['dsr_comm_added'] = 0.00
        return res

    def _calculate_data_rev(self, cr, uid, revenue_id, product, interval_type, line_no, spiff_no_consider):
        tac_master_ids = []
        is_commission = True
        is_spiff = True
        is_added = True
        is_bonus_comm = True
        is_bonus_spiff = True
        revenue_obj = self.pool.get('revenue.generate.master')
        product_obj = self.pool.get('product.product')
        tac_obj = self.pool.get('tac.code.master')
        mul_factor = revenue_obj.browse(cr, uid, revenue_id).dsr_revenue_calc
        spiff_factor = revenue_obj.browse(cr, uid, revenue_id).dsr_phone_spiff
        exclude_scnc = revenue_obj.browse(cr, uid, revenue_id).exclude_scnc
        added_rev = revenue_obj.browse(cr, uid, revenue_id).dsr_added_rev
        bonus_line_spiff = revenue_obj.browse(cr, uid, revenue_id).bonus_line_spiff
        bonus_handset_spiff = revenue_obj.browse(cr, uid, revenue_id).bonus_handset_spiff
        month_acc = product_obj.browse(cr, uid, product).monthly_access
        is_scnc  = product_obj.browse(cr, uid, product).is_scnc
        val = val1 = tot = 0.00
        if is_bonus_comm:
            val = (mul_factor * month_acc) + bonus_line_spiff
        else:
            val = (mul_factor * month_acc)
        if not line_no:
            line_no = 0
        cr.execute("select eligible_commission,eligible_spiff,eligible_added,eligible_bonus_comm,eligible_bonus_spiff from transaction_line_soc_rel where line_no = %s and (soc_code=%s or sub_soc_code=%s)"%(line_no,product,product))
        cal_data = cr.fetchall()
        for cal_data_each in cal_data:
            if cal_data_each:
                is_commission = cal_data_each[0]
                is_spiff = cal_data_each[1]
                is_added = cal_data_each[2]
                is_bonus_comm = cal_data_each[3]
                is_bonus_spiff = cal_data_each[4]

        if exclude_scnc == True:
            if interval_type == 'at_act' and is_scnc == False:
                if is_commission:
                    val = val
                if is_added:
                    val = val + added_rev
            else:
                if is_commission:
                    val = val
        else:
            if is_commission:
                val = val
            if is_added:
                val = val + added_rev
        if is_bonus_spiff:
            val1 = (spiff_factor * month_acc) + bonus_handset_spiff
        else:
            val1 = (spiff_factor * month_acc)
        if spiff_no_consider:
            tot = val
        else:
            if is_spiff:
                tot = val + val1
            else:
                tot = val
        return tot

    def _calculate_data_feature_revenue(self, cr, uid, ids, product, product_type, prod_code_type, context=None):
        tac_record_ids = []
        line = self.browse(cr, uid, ids, context=context)
        spiff_no_consider = False
        revenue_obj = self.pool.get('revenue.generate.master')
        product_obj = self.pool.get('product.product')
        tac_obj = self.pool.get('tac.code.master')
        interval_type = 'after_act'
        # credit_class_type = line.dsr_credit_class.category_type.id
        credit_class_type = False
        dsr_jod = False
        imei = line.dsr_imei_no
        if imei:
            tac_record_ids = tac_obj.search(cr, uid, [('tac_code','=',imei[:8])])
        line_no = line.dsr_line_no.id
        dsr_id = line.product_id.id
        trans_date = self.pool.get('wireless.dsr').browse(cr, uid, dsr_id).dsr_date
        rev_root_ids = revenue_obj.search(cr, uid, [('dsr_prod_type','=',product_type),('dsr_start_date','<=',trans_date),('dsr_end_date','>=',trans_date),('inactive','=',False)])
        if rev_root_ids:
            where_condition = []
            where_condition.append(('id','in',rev_root_ids))
            compare_string = str("")
            if len(rev_root_ids) == 1:
                compare_string += str("= %s"%(rev_root_ids[0]))
            else:
                compare_string += str("in %s"%(tuple(rev_root_ids),))
            cr.execute("select distinct(dsr_activation_type) from revenue_generate_master where id "+compare_string+"")
            master_interval_type = map(lambda x: x[0], cr.fetchall())
            cr.execute("select distinct(dsr_prod_code_type) from revenue_generate_master where id "+compare_string+"")
            master_prod_code_type = map(lambda x: x[0], cr.fetchall())
            cr.execute("select distinct(dsr_rev_product) from revenue_generate_master where id "+compare_string+"")
            master_product_ids = map(lambda x: x[0], cr.fetchall())
            cr.execute("select distinct(dsr_credit_class_type) from revenue_generate_master where id "+compare_string+"")
            master_class_type = map(lambda x: x[0], cr.fetchall())
            
            if interval_type in master_interval_type:
                where_condition.append(('dsr_activation_type','=',interval_type))
            if prod_code_type in master_prod_code_type:
                where_condition.append(('dsr_prod_code_type','=',prod_code_type))
            if credit_class_type in master_class_type:
                where_condition.append(('dsr_credit_class_type','=',credit_class_type))
            if product in master_product_ids:
                where_condition.append(('dsr_rev_product','=',product))
            
            rev_final_ids = revenue_obj.search(cr, uid, where_condition)
            if rev_final_ids:
                compare_string = str("")
                if len(rev_final_ids) == 1:
                    compare_string += str("= %s"%(rev_final_ids[0]))
                else:
                    compare_string += str("in %s"%(tuple(rev_final_ids),))
                if tac_record_ids:
                    cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                            where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = false or rev.is_exclude is null)
                            and rev.dsr_jod = %s and tc.tac_id = %s''',(dsr_jod,tac_record_ids[0]))
                    revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                    if revenue_master_ids:
                        tac_ids = []
                        val = self._calculate_data_rev(cr, uid, revenue_master_ids[0], product, interval_type, line_no, spiff_no_consider)
                        return val
                cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                        where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = true or rev.is_exclude is null)
                        and rev.dsr_jod = %s''',(dsr_jod,))
                revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                if revenue_master_ids:
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(revenue_master_ids[0]))
                    tac_ids = map(lambda x: x[0], cr.fetchall())
                    for tac_record_each in tac_record_ids:
                        if tac_record_each in tac_ids:
                            spiff_no_consider = True
                    val = self._calculate_data_rev(cr, uid, revenue_master_ids[0], product, interval_type, line_no, spiff_no_consider)
                    return val
                cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                        where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = true or rev.is_exclude is null)
                        and (rev.dsr_jod is null or rev.dsr_jod = false)''')
                revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                if revenue_master_ids:
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(revenue_master_ids[0]))
                    tac_ids = map(lambda x: x[0], cr.fetchall())
                    for tac_record_each in tac_record_ids:
                        if tac_record_each in tac_ids:
                            spiff_no_consider = True
                    val = self._calculate_data_rev(cr, uid, revenue_master_ids[0], product, interval_type, line_no, spiff_no_consider)
                    return val
                cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                        where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = false or rev.is_exclude is null)
                        and (rev.dsr_jod is null or rev.dsr_jod = false)''')
                revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                if revenue_master_ids:
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(revenue_master_ids[0]))
                    tac_ids = map(lambda x: x[0], cr.fetchall())
                    for tac_record_each in tac_record_ids:
                        if tac_record_each not in tac_ids:
                            spiff_no_consider = True
                    val = self._calculate_data_rev(cr, uid, revenue_master_ids[0], product, interval_type, line_no, spiff_no_consider)
                    return val
            revenue_base_ids = revenue_obj.search(cr, uid, [('id','in',rev_final_ids),('is_exclude','=',False),('exclude_tac_code','=',False),('dsr_jod','=',False)])
            if revenue_base_ids:
                tac_ids = []
                val = self._calculate_data_rev(cr, uid, revenue_base_ids[0], product, interval_type, line_no, spiff_no_consider)
                return val
        val = 0
        return val

    def _calculate_revenue_upg(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        tac_record_ids = []
        line = self.browse(cr, uid, ids, context=context)
        spiff_no_consider = False
        revenue_obj = self.pool.get('revenue.generate.master')
        product_obj = self.pool.get('product.product')
        tac_obj = self.pool.get('tac.code.master')
        product_type = line.dsr_product_type.id
        # credit_class_type = line.dsr_credit_class.category_type.id
        credit_class_type = False
        product = line.dsr_product_code.id
        dsr_jod = line.dsr_jod
        imei = line.dsr_imei_no
        if imei:
            tac_record_ids = tac_obj.search(cr, uid, [('tac_code','=',imei[:8])])
        line_no = line.dsr_line_no.id
        prod_code_type = self.pool.get('product.product').browse(cr, uid, product).dsr_prod_code_type.id
        phone_purchase = line.dsr_phone_purchase_type
        # dsr_id = line.product_id.id
        cr.execute("select product_id from wireless_dsr_upgrade_line where id=%s"%(line.id,))
        dsr_data_id = cr.fetchall()
        dsr_id = dsr_data_id[0][0]
        trans_date = self.pool.get('wireless.dsr').browse(cr, uid, dsr_id).dsr_date
        rev_root_ids = revenue_obj.search(cr, uid, [('dsr_prod_type','=',product_type),('dsr_start_date','<=',trans_date),('dsr_end_date','>=',trans_date),('inactive','=',False)])
        if rev_root_ids:
            where_condition = []
            where_condition.append(('id','in',rev_root_ids))
            compare_string = str("")
            if len(rev_root_ids) == 1:
                compare_string += str("= %s"%(rev_root_ids[0]))
            else:
                compare_string += str("in %s"%(tuple(rev_root_ids),))
            cr.execute("select distinct(dsr_prod_code_type) from revenue_generate_master where id "+compare_string+"")
            master_prod_code_type = map(lambda x: x[0], cr.fetchall())
            cr.execute("select distinct(dsr_rev_product) from revenue_generate_master where id "+compare_string+"")
            master_product_ids = map(lambda x: x[0], cr.fetchall())
            cr.execute("select distinct(dsr_credit_class_type) from revenue_generate_master where id "+compare_string+"")
            master_class_type = map(lambda x: x[0], cr.fetchall())
            
            if prod_code_type in master_prod_code_type:
                where_condition.append(('dsr_prod_code_type','=',prod_code_type))
            if credit_class_type in master_class_type:
                where_condition.append(('dsr_credit_class_type','=',credit_class_type))
            if product in master_product_ids:
                where_condition.append(('dsr_rev_product','=',product))
            
            rev_final_ids = revenue_obj.search(cr, uid, where_condition)
            if rev_final_ids:
                compare_string = str("")
                if len(rev_final_ids) == 1:
                    compare_string += str("= %s"%(rev_final_ids[0]))
                else:
                    compare_string += str("in %s"%(tuple(rev_final_ids),))
                if tac_record_ids:
                    cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                            where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = false or rev.is_exclude is null)
                            and rev.dsr_jod = %s and tc.tac_id = %s''',(dsr_jod,tac_record_ids[0]))
                    revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                    if revenue_master_ids:
                        tac_ids = []
                        val = self._calculate_rev(cr, uid, revenue_master_ids[0], phone_purchase, product, line_no, spiff_no_consider)
                        return val
                cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                        where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = true or rev.is_exclude is null)
                        and rev.dsr_jod = %s''',(dsr_jod,))
                revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                if revenue_master_ids:
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(revenue_master_ids[0]))
                    tac_ids = map(lambda x: x[0], cr.fetchall())
                    for tac_record_each in tac_record_ids:
                        if tac_record_each in tac_ids:
                            spiff_no_consider = True
                    val = self._calculate_rev(cr, uid, revenue_master_ids[0], phone_purchase, product, line_no, spiff_no_consider)
                    return val
                cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                        where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = true or rev.is_exclude is null)
                        and (rev.dsr_jod is null or rev.dsr_jod = false)''')
                revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                if revenue_master_ids:
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(revenue_master_ids[0]))
                    tac_ids = map(lambda x: x[0], cr.fetchall())
                    for tac_record_each in tac_record_ids:
                        if tac_record_each in tac_ids:
                            spiff_no_consider = True
                    val = self._calculate_rev(cr, uid, revenue_master_ids[0], phone_purchase, product, line_no, spiff_no_consider)
                    return val
                cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                        where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = false or rev.is_exclude is null)
                        and (rev.dsr_jod is null or rev.dsr_jod = false)''')
                revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                if revenue_master_ids:
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(revenue_master_ids[0]))
                    tac_ids = map(lambda x: x[0], cr.fetchall())
                    for tac_record_each in tac_record_ids:
                        if tac_record_each not in tac_ids:
                            spiff_no_consider = True
                    val = self._calculate_rev(cr, uid, revenue_master_ids[0], phone_purchase, product, line_no, spiff_no_consider)
                    return val
            revenue_base_ids = revenue_obj.search(cr, uid, [('id','in',rev_final_ids),('is_exclude','=',False),('exclude_tac_code','=',False),('dsr_jod','=',False)])
            if revenue_base_ids:
                tac_ids = []
                val = self._calculate_rev(cr, uid, revenue_base_ids[0], phone_purchase, product, line_no, spiff_no_consider)
                return val
        val = 0
        return val

    def _calculate_total_upgrade_rev(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            revenue_obj = self.pool.get('revenue.generate.master')
            product_obj = self.pool.get('product.product')
            dsr_id = line.product_id.id
            dsr_data = self.pool.get('wireless.dsr').browse(cr, uid, dsr_id)
            trans_date = dsr_data.dsr_date
            emp_des = dsr_data.dsr_designation_id.id
            comm_percent = 0.00
            base_comm_obj = self.pool.get('comm.basic.commission.formula')
            base_comm_search = base_comm_obj.search(cr, uid, [('comm_designation','=',emp_des),('comm_start_date','<=',trans_date),('comm_end_date','>=',trans_date),('comm_inactive','=',False)])
            if base_comm_search:
                comm_percent = base_comm_obj.browse(cr, uid, base_comm_search[0]).comm_percent
            else:
                base_comm_search = base_comm_obj.search(cr, uid, [('comm_start_date','<=',trans_date),('comm_end_date','>=',trans_date),('comm_inactive','=',False)])
                if base_comm_search:
                    comm_percent = base_comm_obj.browse(cr, uid, base_comm_search[0]).comm_percent
            res[line.id] = {
                            'dsr_tot_rev_gen':0.00,
                            'dsr_tot_comm_per_line':0.00
                            }
            val = 0.00
            # val2 = self._calculate_upgrade_revenue(cr, uid, ids, field_name, arg, context=context)
            # val1 = val2[line.id]['dsr_rev_gen']
            # val = val + val1
            product = line.dsr_product_code.id
            prod_data = product_obj.browse(cr, uid, product)
            product_type = prod_data.categ_id.id
            prod_code_type = prod_data.dsr_prod_code_type.id
            val1 = self._calculate_revenue_upg(cr, uid, line.id, field_name, arg, context=context)
            if val1:
                val = val + val1['tot']
            if line.jump == True:
                jump_soc = line.jump_soc.id
                jump_prod_type = line.jump_soc.categ_id.id
                jump_prod_code_type = line.jump_soc.dsr_prod_code_type.id
                val1 = self._calculate_data_feature_revenue(cr, uid, line.id, jump_soc, jump_prod_type, jump_prod_code_type)
                val = val + val1
            if line.intl_feature == True:
                intl_soc = line.intl_feature_soc.id
                intl_prod_type = line.intl_feature_soc.categ_id.id
                intl_prod_code_type = line.intl_feature_soc.dsr_prod_code_type.id
                val1 = self._calculate_data_feature_revenue(cr, uid, line.id, intl_soc, intl_prod_type, intl_prod_code_type)
                val = val + val1
            if line.data == True:
                data_soc = line.data_soc.id
                data_prod_type = line.data_soc.categ_id.id
                data_prod_code_type = line.data_soc.dsr_prod_code_type.id
                val1 = self._calculate_data_feature_revenue(cr, uid, line.id, data_soc, data_prod_type, data_prod_code_type)
                val = val + val1
            if line.other == True:
                other_soc = line.other_soc.id
                other_prod_type = line.other_soc.categ_id.id
                other_prod_code_type = line.other_soc.dsr_prod_code_type.id
                val1 = self._calculate_data_feature_revenue(cr, uid, line.id, other_soc, other_prod_type, other_prod_code_type)
                val = val + val1
            # if line.messaging == True:
            #     msg_soc = line.msg_soc.id
            #     msg_prod_type = line.msg_soc.categ_id.id
            #     msg_prod_code_type = line.msg_soc.dsr_prod_code_type.id
            #     val1 = self._calculate_data_feature_revenue(cr, uid, line.id, msg_soc, msg_prod_type, msg_prod_code_type)
            #     val = val + val1
            res[line.id]['dsr_tot_rev_gen'] = val
            res[line.id]['dsr_tot_comm_per_line'] = float(val * comm_percent / 100)
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('wireless.dsr.upgrade.line').browse(cr, uid, ids, context=context):
            result[line.id] = True
        return result.keys()
    
    def default_get1(self,cr, uid, fields, context=None):
        #fucnton created by shashank 27/11
        prod_cat_obj=self.pool.get('product.category')
        val=prod_cat_obj.search(cr,uid,[('prod_type','=','upgrade')])
        if val:
            res=val[0]
        return res
       
    _columns = {
                'dsr_product_type':fields.many2one('product.category','Product Type'),
                'dsr_trans_type':fields.selection(_prod_type, 'Transaction Type'),
                ### below product Code type added for testing benefit
                'dsr_product_code_type':fields.many2one('product.category','Product Code Type'),
                # 'dsr_product_code_type':fields.char('Product Code Type', size=64),
                'product_id':fields.many2one('wireless.dsr','Product Id'),
                'dsr_sim_no': fields.char('SIM #', size=25),
                'dsr_cust_ban_no':fields.char('BAN #', size=16),
                'dsr_credit_class':fields.many2one('credit.class', 'Credit class'),
                # 'dsr_credit_class_type':fields.many2one('credit.class.type', 'Credit Class Type'),
                # 'dsr_activiation_interval':fields.many2one('dsr.activation.interval.type','Activation Interval'),
                'dsr_ship_to':fields.boolean('Ship To'),
                'dsr_emp_type':fields.many2one('dsr.employee.type','T-Mobile Employee'),
                'is_emp_upg':fields.boolean('Employee Upgrade'),
                'dsr_p_number':fields.char('P-number'),
                'dsr_line_no':fields.many2one('credit.line.limit', 'Line #'),
                'dsr_imei_no':fields.char('IMEI #', size=15),
                'dsr_product_code':fields.many2one('product.product', 'Product Code'),				
                'is_voice':fields.boolean('Voice Barred'),
                'is_mobile':fields.boolean('Mobile Internet'),
                'is_jump':fields.boolean('JUMP Attached'),
                # 'dsr_product_description':fields.char('Product Description', size=64),
                'dsr_phone_no':fields.char('Mobile Phone', size=10),
                # 'dsr_mob_port':fields.boolean('Mobile # Port'),
                # 'dsr_port_comp':fields.many2one('port.company', 'Port Company'),
                'dsr_temp_no':fields.char('Temporary #', size=10),
                'act_type':fields.selection([('Act','Activation'),('reactivation','Reactivation'),('deactivation','DeActivation')], 'Activation Type'),
                'jump':fields.boolean('JUMP or PHP'),
                'intl_feature':fields.boolean('International Feature'),
                'data':fields.boolean('Data'),
                # 'messaging':fields.boolean('Messaging'),
                'other':fields.boolean('Other'),
                'jump_soc':fields.many2one('product.product','JUMP or PHP SOC code'),
                'intl_feature_soc':fields.many2one('product.product','International Feature SOC code'),
                'data_soc':fields.many2one('product.product','Data SOC code'),
                # 'msg_soc':fields.many2one('product.product','Messaging SOC code'),
                'other_soc':fields.many2one('product.product','Other SOC code'),
                'dsr_jump_already':fields.boolean('JUMP already on Account'),
                'dsr_php_already':fields.boolean('PHP already on Account'),
                'dsr_act_date':fields.date('Activation Date'),
                'pseudo_date':fields.date('Pseudo Transaction Date'),
                'dsr_deact_date':fields.date('DeActivation Date'),
                'act_recon':fields.boolean('Act Reconciled'),
                'deact_recon':fields.boolean('DeAct Reconciled'),
                'dsr_react_date':fields.date('ReActivation Date'),
                'react_recon':fields.boolean('ReAct Reconciled'),
                'dsr_phone_purchase_type':fields.selection([('new_device','EIP'),('device_outright','Device Outright')],'Phone Purchase'),
                'dsr_trade_inn':fields.selection([('yes','Yes'),('no','No')],'Trade-in'),
                'state':fields.selection([('draft','Draft'),('pending','Pending'),('cancel','Cancel'),('done','Done'),('void','VOID')],'State', readonly=True),
                'dsr_eip_no':fields.char('EIP #', size=16),
                # 'state_upgrade':fields.related('product_id', 'state', type='selection', string="State", relation='wireless.dsr', store=True),
                # 'dsr_warranty':fields.char('Warranty Exchange Order #', size=16),
                'dsr_rev_gen':fields.function(_calculate_upgrade_revenue, string="Total Amount", type='float', multi='sums',
                        store=True),
                'dsr_comm_amnt':fields.function(_calculate_upgrade_revenue, string="DSR Commission Amount", type='float', multi='sums',
                        store=True),
                'dsr_comm_spiff':fields.function(_calculate_upgrade_revenue, string="DSR Spiff Amount", type='float', multi='sums',
                        store=True),
                'dsr_comm_added':fields.function(_calculate_upgrade_revenue, string="DSR Added Amount", type='float', multi='sums',
                        store=True),
                'dsr_comm_per_line':fields.function(_calculate_upgrade_revenue, string="Commission per line", type='float', multi='sums',
                    store=True),
                'valid': fields.many2one('crashing.validation.flag','Valid'),
                'dsr_smd':fields.boolean('SMD'),
                'dsr_contract_term':fields.integer('Contract Term'),
                'dsr_monthly_access':fields.float('Monthle Access'),
                'dsr_tot_rev_gen':fields.function(_calculate_total_upgrade_rev, string="Total Rev Gen.", type="float", multi='sums'),
                'dsr_tot_comm_per_line':fields.function(_calculate_total_upgrade_rev, string="Total Commission per line", type='float', multi='sums'),
                'dsr_pmd': fields.boolean('PMD'),
                'comments': fields.text('Reasons For Deactivation of Chargebacks'),
                'noncommissionable':fields.boolean('Non Commissionable'),
                'spiff_amt': fields.float('Spiff Amt'),
                'commission_amt': fields.float('Commissions Amt'),
                'crash_act_date': fields.date('Crashing Activation Date'),
                'crash_deact_date': fields.date('Crashing Deactivation Date'),
                'crash_react_date': fields.date('Crashing Reactivation Date'),
                # 'dsr_crash_activation': fields.many2one('dsr.tmob.crash.process','Activation'),
                # 'dsr_crash_deactivation': fields.many2one('dsr.crash.process.deactivation','Deactivation'),
                'employee_id' : fields.many2one('hr.employee','Emp'),
                'store_id':fields.many2one('sap.store', 'Store'),
                'market_id':fields.many2one('market.place', 'Market'),
                'region_id':fields.many2one('market.regions', 'Region'),
                'eip_phone_purchase':fields.boolean('EIP Phone Purchased'),
                'dsr_phone_first':fields.many2one('phone.type.master', 'Device Type'),
                'dsr_transaction_id':fields.char('Transaction ID', size=64),
                'jump_upgrade':fields.selection([('cihu','CIHU'),('jump','JUMP'),('jod','JUMP on Demand'),('sys_issue','System Issue')],'Upgrade Type'),
                'cihu_no':fields.char('CIHU Order #', size=9),
                'jump_no':fields.char('JUMP Order #', size=64),
                'reliance_no':fields.char('Reliance Ticket #', size=64),
                'dsr_jod':fields.boolean('JUMP on Demand'),
                'customer_name':fields.char('Customer Name', size=1024),
                'dealer_code':fields.char('Dealer Code', size=1024),
                'dsr_exception':fields.boolean('Exception'),
                'dsr_designation_id':fields.many2one('hr.job','Designation')
                #'tmob_comments' : fields.text('Tmobile Comments'),#### field added as per the change to update the T-mobile comments
                #'valid_neutral': fields.many2one('crashing.validation.flag','Valid Non-Zero'),#### field added to be used for nonzero crash
    }
    _defaults = {
                'state':'draft',
                'act_type':'Act',
                'dsr_trans_type':'upgrade',
                'dsr_product_type':default_get1,
                'dsr_exception':False,
                'is_jump':False
    }

    def onchange_emp_type(self, cr, uid, ids, dsr_emp_type):
        emp_obj = self.pool.get('dsr.employee.type')
        is_emp_upg = False
        if dsr_emp_type:
            emp_data = emp_obj.browse(cr, uid, dsr_emp_type)
            if emp_data.is_emp_upg:
                is_emp_upg = True
            return {'value':{'is_emp_upg':is_emp_upg,'dsr_p_number':False,'jump_upgrade':False}}
        return {'value':{'is_emp_upg':is_emp_upg,'dsr_p_number':False,'jump_upgrade':False}}

    def onchange_product(self, cr, uid, ids, product):        
        prod_obj = self.pool.get('product.product')
        domain = {'data_soc':  [('is_data','=',True),('dsr_categ_id','=','feature')]}
        if product:
            prod_data = prod_obj.browse(cr, uid, product)
            prod_code_type = prod_data.dsr_prod_code_type.id
            monthly_access = prod_data.monthly_access
            contract_term = prod_data.contract_term
            vals = {'dsr_product_code_type':prod_code_type,
                    'dsr_monthly_access':monthly_access,
                    'dsr_contract_term':contract_term,
                    'data_soc':False,
                    'data':False
                    }
            cr.execute("select data_soc_id from product_business_rule where main_soc_id = %s and active = true"%(product))
            prod_rule_ids = map(lambda x: x[0], cr.fetchall())
            domain['data_soc'] += [('id','in',prod_rule_ids)]
            return {'value':vals,'domain':domain}
        vals = {
                'dsr_product_code_type':False,
                'dsr_monthly_access':False,
                'dsr_contract_term':False,
                'data_soc':False,
                'data':False
        }
        return {'value':vals,'domain':domain}

    def onchange_data_soc(self, cr, uid, ids, data_soc, main_prod):
        vals = {}
        if main_prod and data_soc:
            cr.execute("select main_soc_id from product_business_rule where data_soc_id = %s and active = true"%(data_soc,))
            product_search_ids = map(lambda x: x[0], cr.fetchall())
            if main_prod not in product_search_ids:
                vals = {'dsr_product_code':False}
            return {'value':vals}
        return {}

    def onchange_cihu(self, cr, uid, ids, cihu_no):
        if cihu_no:
            validate_cihu(cihu_no)
        return {}

#    def onchange_jump_no(self, cr, uid, ids, jump_no):
#        if jump_no:
#            validate_cihu(jump_no)
#        return {}

#    def onchange_reliance_no(self, cr, uid, ids, reliance_no):
#        if reliance_no:
#            validate_cihu(reliance_no)
#        return {}

    def onchange_jump_upgrade(self, cr, uid, ids, jump_upgrade):
        if jump_upgrade == 'cihu':
            return {'value':{'jump_no':False,'reliance_no':False,'dsr_jod':False,'dsr_phone_purchase_type':False,'dsr_jump_already':False}}
        elif jump_upgrade == 'jump':
            return {'value':{'cihu_no':False,'reliance_no':False,'dsr_jod':False,'dsr_phone_purchase_type':False,'dsr_jump_already':False}}
        elif jump_upgrade == 'jod':
            return {'value':{'cihu_no':False,'reliance_no':False,'dsr_jod':True,'dsr_phone_purchase_type':'new_device'}}
        elif jump_upgrade == 'sys_issue':
            return {'value':{'cihu_no':False,'jump_no':False,'dsr_jod':False,'dsr_phone_purchase_type':False,'dsr_jump_already':False}}
        else:
            return {'value':{'cihu_no':False,'jump_no':False,'reliance_no':False,'dsr_jod':False,'dsr_phone_purchase_type':False,'dsr_jump_already':False}}

    def onchange_jump(self, cr, uid, ids, jump):
        if not jump:
            return {'value':{'jump_soc':False}}
        return {}

    def onchange_jump_soc(self, cr, uid, ids, jump_soc):
        prod_obj = self.pool.get('product.product')
        if jump_soc:
            jump = prod_obj.browse(cr, uid, jump_soc).is_jump
            return {'value':{'is_jump':jump}}
        return {'value':{'is_jump':False}}

    def onchange_jump_already(self, cr, uid, ids, jump):
        return {'value':{'jump':False,'jump_soc':False,'dsr_jod':False}}

    def onchange_php_already(self, cr, uid, ids, jump):
        return {'value':{'jump':False,'jump_soc':False}}    
        
    def onchange_phone_purchase(self, cr, uid, ids, phone_purchase, dsr_jod, jump_upgrade):
        vals = {
                'dsr_eip_no':False,
                'dsr_trade_inn':False,
                'dsr_jod':False
        }
        if jump_upgrade == 'jod':
            vals.update({'jump_upgrade':False})
        domain = {'jump_soc':['|',('is_php','=',True),('is_jump','=',True),('dsr_categ_id','=','feature')]}
        if phone_purchase:
            if phone_purchase == 'device_outright':
                vals = {
                        'dsr_eip_no':False,
                        'dsr_trade_inn':False,
                        'jump':False,
                        'other':False,
                        'jump_soc':False,
                        'other_soc':False,
                        'dsr_jod':False
                }
                if jump_upgrade == 'jod':
                    vals.update({'jump_upgrade':False})
                domain = {
                        'jump_soc':[('is_php','=',True),('dsr_categ_id','=','feature')]
                }
            elif phone_purchase == 'new_device':
                vals = {
                        'jump':False,
                        'jump_soc':False,
                        'other':False,
                        'other_soc':False
                }
                if dsr_jod:
                    domain = {
                             'jump_soc':[('is_php','=',True),('dsr_categ_id','=','feature')]
                    }
                else:
                    domain = {
                             'jump_soc':['|',('is_php','=',True),('is_jump','=',True),('dsr_categ_id','=','feature')]
                    }
            return {'value':vals,'domain':domain}
        return {'value':vals}

    def onchange_product_type(self, cr, uid, ids, product_type):
        if product_type:
            return {'value': {'dsr_product_code' : False}}
        return {}

    def onchange_data(self, cr, uid, ids, data):
        if not data:
            return {'value':{'data_soc':False}}
        return {}

    def onchange_intl_feature(self, cr, uid, ids, intl_feature):
        if not intl_feature:
            return {'value':{'intl_feature_soc':False}}
        return {}

    def onchange_other(self, cr, uid, ids, other):
        if not other:
            return {'value':{'other_soc':False}}
        return {}

    def onchange_messaging(self, cr, uid, ids, messaging):
        if messaging:
            return {'value':{'msg_soc':False}}
        return {}

    def onchange_phone(self, cr, uid, ids, phone):
        if phone:
            phone_check(phone)
            return {}
        return {}

    def onchange_sim(self, cr, uid, ids, sim):
        if sim:
            sim_validation(sim)
            return {}
        return {}

    def onchange_imei(self, cr, uid, ids, imei):
        if imei:
            imei_check(imei)
            return {}
        return {}

    def _create_data_feature(self, cr, uid, vals, res):
        prod_obj = self.pool.get('product.product')
        # cc_obj = self.pool.get('credit.class')
        # cc_data_browse = cc_obj.browse(cr, uid, vals['dsr_credit_class'])
        upgrade_feature_obj = self.pool.get('wireless.dsr.feature.line')
        if vals['jump'] and vals['jump_soc']:
            prod_jump_browse = prod_obj.browse(cr, uid, vals['jump_soc'])
            jump_data = {   'dsr_product_code' : vals['jump_soc'],
                            'feature_product_id':vals['product_id'],
                            'dsr_eip_no':vals['dsr_eip_no'],
                            # 'dsr_warranty':vals['dsr_warranty'],
                            'dsr_jump':True,
                            'dsr_product_type':prod_jump_browse.categ_id.id,
                            'dsr_product_code_type' : prod_jump_browse.dsr_prod_code_type.id,
                            'dsr_monthly_access':prod_jump_browse.monthly_access,
                            'dsr_contract_term':prod_jump_browse.contract_term,
                            # 'dsr_product_description' : prod_jump_browse.name,
                            'dsr_phone_no' : vals['dsr_phone_no'],
                            'dsr_cust_ban_no' : vals['dsr_cust_ban_no'],
                            'dsr_sim_no' : vals['dsr_sim_no'],
                            'dsr_imei_no' : vals['dsr_imei_no'],
                            'dsr_emp_type':vals['dsr_emp_type'],
                            'is_emp_upg':vals['is_emp_upg'],
                            'dsr_p_number':vals['dsr_p_number'],
                            'dsr_line_no':vals.get('dsr_line_no'),
                            'dsr_jod':vals.get('dsr_jod'),
                            # 'dsr_credit_class' : vals['dsr_credit_class'],
                            # 'dsr_credit_class_type' : cc_data_browse.category_type.id,
                            'dsr_activiation_interval' : 'after_act',
                            'created_upgrade':True,
                            'upgrade_id' : res,
                            'dsr_phone_purchase_type':vals['dsr_phone_purchase_type'],
                            'dsr_trade_inn':vals['dsr_trade_inn'],
                            'dsr_ship_to':vals['dsr_ship_to']
                        }
            upgrade_feature_obj.create(cr, uid, jump_data)
        if vals['data'] and vals['data_soc']:
            prod_data_browse = prod_obj.browse(cr, uid, vals['data_soc'])
            data = {    'dsr_product_code' : vals['data_soc'],
                        'feature_product_id':vals['product_id'],
                        'dsr_eip_no':vals['dsr_eip_no'],
                        # 'dsr_warranty':vals['dsr_warranty'],
                        'dsr_product_type':prod_data_browse.categ_id.id,
                        'dsr_product_code_type' : prod_data_browse.dsr_prod_code_type.id,
                        'dsr_monthly_access':prod_data_browse.monthly_access,
                        'dsr_contract_term':prod_data_browse.contract_term,
                        # 'dsr_product_description' : prod_data_browse.name,
                        'dsr_phone_no' : vals['dsr_phone_no'],
                        'dsr_cust_ban_no' : vals['dsr_cust_ban_no'],
                        'dsr_sim_no' : vals['dsr_sim_no'],
                        'dsr_imei_no' : vals['dsr_imei_no'],
                        'dsr_emp_type':vals['dsr_emp_type'],
                        'is_emp_upg':vals['is_emp_upg'],
                        'dsr_p_number':vals['dsr_p_number'],
                        'dsr_line_no':vals.get('dsr_line_no'),
                            'dsr_jod':vals.get('dsr_jod'),
                        # 'dsr_credit_class' : vals['dsr_credit_class'],
                        # 'dsr_credit_class_type' : cc_data_browse.category_type.id,
                        'dsr_activiation_interval' : 'after_act',
                        'created_upgrade':True,
                        'upgrade_id' : res,
                        'dsr_phone_purchase_type':vals['dsr_phone_purchase_type'],
                        'dsr_trade_inn':vals['dsr_trade_inn'],
                        'dsr_ship_to':vals['dsr_ship_to']
                    }
            upgrade_feature_obj.create(cr, uid, data)
        if vals['intl_feature'] and vals['intl_feature_soc']:
            prod_intl_feature_browse = prod_obj.browse(cr, uid, vals['intl_feature_soc'])
            intl_feature_data = {'dsr_product_code' : vals['intl_feature_soc'],
                                'feature_product_id':vals['product_id'],
                                'dsr_eip_no':vals['dsr_eip_no'],
                                # 'dsr_warranty':vals['dsr_warranty'],
                                'dsr_product_type':prod_intl_feature_browse.categ_id.id,
                                'dsr_product_code_type' : prod_intl_feature_browse.dsr_prod_code_type.id,
                                'dsr_monthly_access':prod_intl_feature_browse.monthly_access,
                                'dsr_contract_term':prod_intl_feature_browse.contract_term,
                                # 'dsr_product_description' : prod_intl_feature_browse.name,
                                'dsr_phone_no' : vals['dsr_phone_no'],
                                'dsr_cust_ban_no' : vals['dsr_cust_ban_no'],
                                'dsr_sim_no' : vals['dsr_sim_no'],
                                'dsr_imei_no' : vals['dsr_imei_no'],
                                'dsr_emp_type':vals['dsr_emp_type'],
                                'is_emp_upg':vals['is_emp_upg'],
                                'dsr_p_number':vals['dsr_p_number'],
                                'dsr_line_no':vals.get('dsr_line_no'),
                                'dsr_jod':vals.get('dsr_jod'),
                                # 'dsr_credit_class' : vals['dsr_credit_class'],
                                # 'dsr_credit_class_type' : cc_data_browse.category_type.id,
                                'dsr_activiation_interval' : 'after_act',
                                'created_upgrade':True,
                                'upgrade_id' : res,
                                'dsr_phone_purchase_type':vals['dsr_phone_purchase_type'],
                                'dsr_trade_inn':vals['dsr_trade_inn'],
                                'dsr_ship_to':vals['dsr_ship_to']
                            }
            upgrade_feature_obj.create(cr, uid, intl_feature_data)
        if vals['other'] and vals['other_soc']:            
            prod_other_browse = prod_obj.browse(cr, uid, vals['other_soc'])
            other_data = {  'dsr_product_code' : vals['other_soc'],
                            'feature_product_id':vals['product_id'],
                            'dsr_eip_no':vals['dsr_eip_no'],
                            # 'dsr_warranty':vals['dsr_warranty'],
                            'dsr_product_type':prod_other_browse.categ_id.id,
                            'dsr_product_code_type' : prod_other_browse.dsr_prod_code_type.id,
                            'dsr_monthly_access':prod_other_browse.monthly_access,
                            'dsr_contract_term':prod_other_browse.contract_term,
                            # 'dsr_product_description' : prod_other_browse.name,
                            'dsr_phone_no' : vals['dsr_phone_no'],
                            'dsr_cust_ban_no' : vals['dsr_cust_ban_no'],
                            'dsr_sim_no' : vals['dsr_sim_no'],
                            'dsr_imei_no' : vals['dsr_imei_no'],
                            'dsr_emp_type':vals['dsr_emp_type'],
                            'is_emp_upg':vals['is_emp_upg'],
                            'dsr_p_number':vals['dsr_p_number'],
                            'dsr_line_no':vals.get('dsr_line_no'),
                            'dsr_jod':vals.get('dsr_jod'),
                            # 'dsr_credit_class' : vals['dsr_credit_class'],
                            # 'dsr_credit_class_type' : cc_data_browse.category_type.id,
                            'dsr_activiation_interval' : 'after_act',
                            'created_upgrade':True,
                            'upgrade_id' : res,
                            'dsr_phone_purchase_type':vals['dsr_phone_purchase_type'],
                            'dsr_trade_inn':vals['dsr_trade_inn'],
                            'dsr_ship_to':vals['dsr_ship_to']
                            }
            upgrade_feature_obj.create(cr, uid, other_data)
        return True

    def check_jump_score_php(self, cr, uid, phone_purchase, jump_soc, other_soc, jump_already, php_already, dsr_jod):
        prod_obj = self.pool.get('product.product')
        jump_soc = prod_obj.browse(cr, uid, jump_soc)
        other_soc = prod_obj.browse(cr, uid, other_soc)
        if phone_purchase == 'new_device':
            if jump_soc and other_soc:
                if other_soc.is_score:
                    raise osv.except_osv(('Warning!!'),('You can have only JUMP/PHP or Score attached with EIP phone purchase type in Upgrade Line.'))
            elif dsr_jod and jump_soc.is_jump:
                raise osv.except_osv(('Warning!!'),('You cannot have JUMP SOC attached, if JUMP on Demand is selected.'))
            elif (jump_already or php_already) and other_soc:
                if other_soc.is_score:
                    raise osv.except_osv(('Warning!!'),('You cannot have Score attached with JUMP already on account Upgrade Line.'))        
        elif phone_purchase == 'device_outright':
            if jump_soc and other_soc:
                if other_soc.is_score:
                    raise osv.except_osv(('Warning!!'),('You can have only PHP or Score attached with Device Outright phone purchase type in Upgrade Line.'))
            elif (jump_already or php_already) and other_soc:
                if other_soc.is_score:
                    raise osv.except_osv(('Warning!!'),('You cannot have Score attached with JUMP already on account Upgrade Line.'))
            elif jump_soc:
                if jump_soc.is_jump:
                    raise osv.except_osv(('Warning!!'),('You cannot have JUMP attached with Device Outright phone purchase type in Upgrade Line.'))
        return True

    def create(self, cr, uid, vals, context=None):
        res = super(wireless_dsr_upgrade_line, self).create(cr, uid, vals, context=context)
        if 'dsr_imei_no' in vals:
            number = vals['dsr_imei_no']
            imei_check(number)
        if 'dsr_sim_no' in vals:
            card_number = vals['dsr_sim_no']
            sim_validation(card_number)
        if 'dsr_phone_no' in vals:
            phone = vals['dsr_phone_no']
            phone_check(phone)
        if 'cihu_no' in vals:
            cihu = vals['cihu_no']
            validate_cihu(cihu)
        jump_soc = vals['jump_soc']
        other_soc = vals['other_soc']
        phone_purchase = vals['dsr_phone_purchase_type']
        jump_already = vals['dsr_jump_already']
        php_already = vals['dsr_php_already']
        dsr_jod = vals['dsr_jod']
        self.check_jump_score_php(cr, uid, phone_purchase, jump_soc, other_soc, jump_already, php_already, dsr_jod)
#        if 'jump_no' in vals:
#            jump = vals['jump_no']
#            validate_cihu(jump)
#        if 'reliance_no' in vals:
#            reliance = vals['reliance_no']
#            validate_cihu(reliance)
        if vals['data'] or vals['jump'] or vals['intl_feature'] or vals['other']:
            self._create_data_feature(cr, uid, vals, res)
        return res

    def _update_data_feature(self, cr, uid, ids, vals):        
        feature_obj = self.pool.get('wireless.dsr.feature.line')
        prod_obj = self.pool.get('product.product')
        pos_data = self.browse(cr, uid, ids[0])
        imei = pos_data.dsr_imei_no
        phone = pos_data.dsr_phone_no
        sim = pos_data.dsr_sim_no
        product_id = pos_data.product_id.id
        eip_no = pos_data.dsr_eip_no
        ban_no = pos_data.dsr_cust_ban_no
        # credit_class = pos_data.dsr_credit_class.id
        dsr_phone_purchase_type = pos_data.dsr_phone_purchase_type
        dsr_trade_inn = pos_data.dsr_trade_inn
        dsr_ship_to = pos_data.dsr_ship_to
        dsr_emp_type = pos_data.dsr_emp_type.id
        dsr_line_no = pos_data.dsr_line_no.id
        is_emp_upg = pos_data.is_emp_upg
        dsr_p_number = pos_data.dsr_p_number
        dsr_jod = pos_data.dsr_jod
        if 'jump' in vals:
            if vals['jump'] == False:
                jump_code = pos_data.jump_soc.id
                jump_search_ids = feature_obj.search(cr, uid, [('upgrade_id','=',ids[0]),('dsr_product_code','=',jump_code),('dsr_activiation_interval','=','after_act'),('created_upgrade','=',True),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
                if jump_search_ids:
                    feature_obj.unlink(cr, uid, jump_search_ids)
        if 'data' in vals:
            if vals['data'] == False:
                data_code = pos_data.data_soc.id
                data_search_ids = feature_obj.search(cr, uid, [('upgrade_id','=',ids[0]),('dsr_product_code','=',data_code),('dsr_activiation_interval','=','after_act'),('created_upgrade','=',True),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
                if data_search_ids:
                    feature_obj.unlink(cr, uid, data_search_ids)
        if 'intl_feature' in vals:
            if vals['intl_feature'] == False:
                intl_code = pos_data.intl_feature_soc.id
                intl_search_ids = feature_obj.search(cr, uid, [('upgrade_id','=',ids[0]),('dsr_product_code','=',intl_code),('dsr_activiation_interval','=','after_act'),('created_upgrade','=',True),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
                if intl_search_ids:
                    feature_obj.unlink(cr, uid, intl_search_ids)
        # if 'messaging' in vals:
        #     if vals['messaging'] == False:
        #         msg_code = pos_data.msg_soc.id
        #         msg_search_ids = feature_obj.search(cr, uid, [('dsr_product_code','=',msg_code),('dsr_activiation_interval','=','after_act'),('created_upgrade','=',True),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
        #         if msg_search_ids:
        #             feature_obj.unlink(cr, uid, msg_search_ids)
        if 'other' in vals:
            if vals['other'] == False:
                other_code = pos_data.other_soc.id
                other_search_ids = feature_obj.search(cr, uid, [('upgrade_id','=',ids[0]),('dsr_product_code','=',other_code),('dsr_activiation_interval','=','after_act'),('created_upgrade','=',True),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
                if other_search_ids:
                    feature_obj.unlink(cr, uid, other_search_ids)
        if 'jump_soc' in vals:
            jump_code = pos_data.jump_soc.id
            jump_search_ids = feature_obj.search(cr, uid, [('upgrade_id','=',ids[0]),('dsr_product_code','=',jump_code),('dsr_activiation_interval','=','after_act'),('created_upgrade','=',True),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
            if jump_search_ids:
                feature_obj.unlink(cr, uid, jump_search_ids)
            prod_jump_browse = prod_obj.browse(cr, uid, vals['jump_soc'])
            if vals['jump_soc']:
                jump_data = {   'dsr_product_code' : vals['jump_soc'],
                                'feature_product_id':product_id,
                                'dsr_product_type':prod_jump_browse.categ_id.id,
                                'dsr_product_code_type' : prod_jump_browse.dsr_prod_code_type.id,
                                'dsr_monthly_access':prod_jump_browse.monthly_access,
                                'dsr_contract_term':prod_jump_browse.contract_term,
                                'dsr_eip_no':eip_no,
                                'dsr_jump':True,
                                'dsr_phone_no' : phone,
                                'dsr_cust_ban_no' : ban_no,
                                'dsr_sim_no' : sim,
                                'dsr_imei_no' : imei,
                                'dsr_activiation_interval' : 'after_act',
                                'dsr_emp_type':dsr_emp_type,
                                'is_emp_upg':is_emp_upg,
                                'dsr_p_number':dsr_p_number,
                                'dsr_line_no':dsr_line_no,
                                'dsr_jod':dsr_jod,
                                # 'dsr_credit_class' : credit_class,
                                'created_upgrade':True,
                                'upgrade_id' : ids[0],
                                'dsr_phone_purchase_type':dsr_phone_purchase_type,
                                'dsr_trade_inn':dsr_trade_inn,
                                'dsr_ship_to':dsr_ship_to
                            }
                self.pool.get('wireless.dsr.feature.line').create(cr, uid, jump_data)
        if 'data_soc' in vals:
            data_code = pos_data.data_soc.id
            data_search_ids = feature_obj.search(cr, uid, [('upgrade_id','=',ids[0]),('dsr_product_code','=',data_code),('dsr_activiation_interval','=','after_act'),('created_upgrade','=',True),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
            if data_search_ids:
                feature_obj.unlink(cr, uid, data_search_ids)
            prod_data_browse = prod_obj.browse(cr, uid, vals['data_soc'])
            if vals['data_soc']:
                data = {        'dsr_product_code' : vals['data_soc'],
                                'feature_product_id':product_id,
                                'dsr_product_type':prod_data_browse.categ_id.id,
                                'dsr_product_code_type' : prod_data_browse.dsr_prod_code_type.id,
                                'dsr_monthly_access':prod_data_browse.monthly_access,
                                'dsr_contract_term':prod_data_browse.contract_term,
                                'dsr_eip_no':eip_no,
                                'dsr_jump':True,
                                'dsr_phone_no' : phone,
                                'dsr_cust_ban_no' : ban_no,
                                'dsr_sim_no' : sim,
                                'dsr_imei_no' : imei,
                                'dsr_activiation_interval' : 'after_act',
                                'dsr_emp_type':dsr_emp_type,
                                'is_emp_upg':is_emp_upg,
                                'dsr_p_number':dsr_p_number,
                                'dsr_line_no':dsr_line_no,
                                'dsr_jod':dsr_jod,
                                # 'dsr_credit_class' : credit_class,
                                'created_upgrade':True,
                                'upgrade_id' : ids[0],
                                'dsr_phone_purchase_type':dsr_phone_purchase_type,
                                'dsr_trade_inn':dsr_trade_inn,
                                'dsr_ship_to':dsr_ship_to
                            }
                self.pool.get('wireless.dsr.feature.line').create(cr, uid, data)
        if 'intl_feature_soc' in vals:
            intl_feature_code = pos_data.intl_feature_soc.id
            intl_feature_search_ids = feature_obj.search(cr, uid, [('upgrade_id','=',ids[0]),('dsr_product_code','=',intl_feature_code),('dsr_activiation_interval','=','after_act'),('created_upgrade','=',True),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
            if intl_feature_search_ids:
                feature_obj.unlink(cr, uid, intl_feature_search_ids)
            prod_intl_feature_browse = prod_obj.browse(cr, uid, vals['intl_feature_soc'])
            if vals['intl_feature_soc']:
                intl_feature_data = {   'dsr_product_code' : vals['intl_feature_soc'],
                                'feature_product_id':product_id,
                                'dsr_product_type':prod_intl_feature_browse.categ_id.id,
                                'dsr_product_code_type' : prod_intl_feature_browse.dsr_prod_code_type.id,
                                'dsr_monthly_access':prod_intl_feature_browse.monthly_access,
                                'dsr_contract_term':prod_intl_feature_browse.contract_term,
                                'dsr_eip_no':eip_no,
                                'dsr_jump':True,
                                'dsr_phone_no' : phone,
                                'dsr_cust_ban_no' : ban_no,
                                'dsr_sim_no' : sim,
                                'dsr_imei_no' : imei,
                                'dsr_activiation_interval' : 'after_act',
                                'dsr_emp_type':dsr_emp_type,
                                'is_emp_upg':is_emp_upg,
                                'dsr_p_number':dsr_p_number,
                                'dsr_line_no':dsr_line_no,
                                'dsr_jod':dsr_jod,
                                # 'dsr_credit_class' : credit_class,
                                'created_upgrade':True,
                                'upgrade_id' : ids[0],
                                'dsr_phone_purchase_type':dsr_phone_purchase_type,
                                'dsr_trade_inn':dsr_trade_inn,
                                'dsr_ship_to':dsr_ship_to
                            }
                self.pool.get('wireless.dsr.feature.line').create(cr, uid, intl_feature_data)
        if 'other_soc' in vals:
            other_code = pos_data.other_soc.id
            other_search_ids = feature_obj.search(cr, uid, [('upgrade_id','=',ids[0]),('dsr_product_code','=',other_code),('dsr_activiation_interval','=','after_act'),('created_upgrade','=',True),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
            if other_search_ids:
                feature_obj.unlink(cr, uid, other_search_ids)
            prod_other_browse = prod_obj.browse(cr, uid, vals['other_soc'])
            if vals['other_soc']:
                other_data = {  'dsr_product_code' : vals['other_soc'],
                                'feature_product_id':product_id,
                                'dsr_product_type':prod_other_browse.categ_id.id,
                                'dsr_product_code_type' : prod_other_browse.dsr_prod_code_type.id,
                                'dsr_monthly_access':prod_other_browse.monthly_access,
                                'dsr_contract_term':prod_other_browse.contract_term,
                                'dsr_eip_no':eip_no,
                                'dsr_jump':True,
                                'dsr_phone_no' : phone,
                                'dsr_cust_ban_no' : ban_no,
                                'dsr_sim_no' : sim,
                                'dsr_imei_no' : imei,
                                'dsr_activiation_interval' : 'after_act',
                                'dsr_emp_type':dsr_emp_type,
                                'is_emp_upg':is_emp_upg,
                                'dsr_p_number':dsr_p_number,
                                'dsr_line_no':dsr_line_no,
                                'dsr_jod':dsr_jod,
                                # 'dsr_credit_class' : credit_class,
                                'created_upgrade':True,
                                'upgrade_id' : ids[0],
                                'dsr_phone_purchase_type':dsr_phone_purchase_type,
                                'dsr_trade_inn':dsr_trade_inn,
                                'dsr_ship_to':dsr_ship_to
                            }
                self.pool.get('wireless.dsr.feature.line').create(cr, uid, other_data)
        df_search = feature_obj.search(cr, uid, [('upgrade_id','=',ids[0])])
        # if 'dsr_credit_class' in vals:
        #     if df_search:
        #         for df_search_id in df_search:
        #             feature_obj.write(cr, uid, [df_search_id], {'dsr_credit_class':vals['dsr_credit_class']})
        if 'dsr_line_no' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_line_no':vals['dsr_line_no']})
        if 'dsr_p_number' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_p_number':vals['dsr_p_number']})
        if 'is_emp_upg' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'is_emp_upg':vals['is_emp_upg']})
        if 'dsr_emp_type' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_emp_type':vals['dsr_emp_type']})
        if 'dsr_jod' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_jod':vals['dsr_jod']})
        if 'dsr_phone_purchase_type' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_phone_purchase_type':vals['dsr_phone_purchase_type']})
        if 'dsr_eip_no' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_eip_no':vals['dsr_eip_no']})
        if 'dsr_phone_no' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_phone_no':vals['dsr_phone_no']})
        if 'dsr_cust_ban_no' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_cust_ban_no':vals['dsr_cust_ban_no']})
        if 'dsr_sim_no' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_sim_no':vals['dsr_sim_no']})
        if 'dsr_imei_no' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_imei_no':vals['dsr_imei_no']})
        if 'dsr_trade_inn' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_trade_inn':vals['dsr_trade_inn']})
        if 'dsr_ship_to' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_ship_to':vals['dsr_ship_to']})
        return True

    def write(self, cr, uid, ids, vals, context=None):
        for id in ids:
            self_obj = self.browse(cr, uid, id)            
            if 'dsr_imei_no' in vals:
                number = vals['dsr_imei_no']
                imei_check(number)
            if 'dsr_sim_no' in vals:
                card_number = vals['dsr_sim_no']
                sim_validation(card_number)
            if 'dsr_phone_no' in vals:
                phone = vals['dsr_phone_no']
                phone_check(phone)
            if 'cihu_no' in vals:
                cihu = vals['cihu_no']
                validate_cihu(cihu)
            if 'dsr_phone_purchase_type' in vals:
                phone_purchase = vals['dsr_phone_purchase_type']
            else:
                phone_purchase = self_obj.dsr_phone_purchase_type
            if 'jump_soc' in vals:
                jump_soc = vals['jump_soc']
            else:
                jump_soc = self_obj.jump_soc.id
            if 'other_soc' in vals:
                other_soc = vals['other_soc']
            else:
                other_soc = self_obj.other_soc.id
            if 'dsr_jod' in vals:
                dsr_jod = vals['dsr_jod']
            else:
                dsr_jod = self_obj.dsr_jod
    #        if 'jump_no' in vals:
    #            jump = vals['jump_no']
    #            validate_cihu(jump)
    #        if 'reliance_no' in vals:
    #            reliance = vals['reliance_no']
    #            validate_cihu(reliance)
            if 'state' in vals:
                state = vals['state']
            else:
                state = self_obj.state
            if 'dsr_jump_already' in vals:
                dsr_jump_already = vals['dsr_jump_already']
            else:
                dsr_jump_already = self_obj.dsr_jump_already
            php_already = vals.get('dsr_php_already')
            if not php_already:
                php_already = self_obj.dsr_php_already
            if state != 'draft':
               self.check_jump_score_php(cr, uid, phone_purchase, jump_soc, other_soc, dsr_jump_already, php_already, dsr_jod)
            self._update_data_feature(cr, uid, [id], vals)
            res = super(wireless_dsr_upgrade_line, self).write(cr, uid, ids, vals, context=context)
        return res

    def unlink(self, cr, uid, ids, context=None):
        feature_obj = self.pool.get('wireless.dsr.feature.line')
        pos_data = self.browse(cr, uid, ids[0])        
        imei = pos_data.dsr_imei_no
        phone = pos_data.dsr_phone_no
        sim = pos_data.dsr_sim_no
        if pos_data.jump == True:
            jump_code = pos_data.jump_soc.id
            jump_search_ids = feature_obj.search(cr, uid, [('upgrade_id','=',ids[0]),('dsr_product_code','=',jump_code),('dsr_activiation_interval','=','after_act'),('created_upgrade','=',True),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
            if jump_search_ids:
                feature_obj.unlink(cr, uid, jump_search_ids)
        if pos_data.data == True:
            data_code = pos_data.data_soc.id
            data_search_ids = feature_obj.search(cr, uid, [('upgrade_id','=',ids[0]),('dsr_product_code','=',data_code),('dsr_activiation_interval','=','after_act'),('created_upgrade','=',True),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
            if data_search_ids:
                feature_obj.unlink(cr, uid, data_search_ids)
        if pos_data.intl_feature == True:
            intl_code = pos_data.intl_feature_soc.id
            intl_search_ids = feature_obj.search(cr, uid, [('upgrade_id','=',ids[0]),('dsr_product_code','=',intl_code),('dsr_activiation_interval','=','after_act'),('created_upgrade','=',True),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
            if intl_search_ids:
                feature_obj.unlink(cr, uid, intl_search_ids)
        # if pos_data.messaging == True:
        #     msg_code = pos_data.msg_soc.id
        #     msg_search_ids = feature_obj.search(cr, uid, [('dsr_product_code','=',msg_code),('dsr_activiation_interval','=','after_act'),('created_upgrade','=',True),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
        #     if msg_search_ids:
        #         feature_obj.unlink(cr, uid, msg_search_ids)
        if pos_data.other == True:
            other_code = pos_data.other_soc.id
            other_search_ids = feature_obj.search(cr, uid, [('upgrade_id','=',ids[0]),('dsr_product_code','=',other_code),('dsr_activiation_interval','=','after_act'),('created_upgrade','=',True),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
            if other_search_ids:
                feature_obj.unlink(cr, uid, other_search_ids)
        res = super(wireless_dsr_upgrade_line, self).unlink(cr, uid, ids, context=context)
        return res
        
wireless_dsr_upgrade_line()

class crashing_validation_flag(osv.osv):
    _name = 'crashing.validation.flag'
    _description = "Validation Flag"
    _columns = {
                'flag':fields.char('Flag'),
    }
    _rec_name = 'flag'
crashing_validation_flag()

################## DSR Postpaid Line Entry ###############################
class wireless_dsr_postpaid_line(osv.osv):
    _name = 'wireless.dsr.postpaid.line'
    _description = "Wireless DSR Postpaid Line"
    _order = 'id desc'

    def _calculate_rev(self, cr, uid, revenue_id, phone_purchase, product, line_no, spiff_no_consider):
        val = {}
        tac_master_ids = []
        is_commission = True
        is_spiff = True
        is_added = True
        is_bonus_comm = True
        is_bonus_spiff = True
        revenue_obj = self.pool.get('revenue.generate.master')
        product_obj = self.pool.get('product.product')
        tac_obj = self.pool.get('tac.code.master')
        mul_factor = revenue_obj.browse(cr, uid, revenue_id).dsr_revenue_calc
        spiff_factor = revenue_obj.browse(cr, uid, revenue_id).dsr_phone_spiff
        added_rev = revenue_obj.browse(cr, uid, revenue_id).dsr_added_rev
        bonus_line_spiff = revenue_obj.browse(cr, uid, revenue_id).bonus_line_spiff
        bonus_handset_spiff = revenue_obj.browse(cr, uid, revenue_id).bonus_handset_spiff
        month_acc = product_obj.browse(cr, uid, product).monthly_access
        if not line_no:
            line_no = 0
        cr.execute("select eligible_commission,eligible_spiff,eligible_added,eligible_bonus_comm,eligible_bonus_spiff from transaction_line_soc_rel where line_no = %s and (soc_code=%s or sub_soc_code=%s)"%(line_no,product,product))
        cal_data = cr.fetchall()
        for cal_data_each in cal_data:
            if cal_data_each:
                is_commission = cal_data_each[0]
                is_spiff = cal_data_each[1]
                is_added = cal_data_each[2]
                is_bonus_comm = cal_data_each[3]
                is_bonus_spiff = cal_data_each[4]
        val = {
                'comm':0.00,
                'spiff':0.00,
                'added':0.00,
                'tot':0.00,
        }
        if is_bonus_comm:
            val['comm'] = (mul_factor * month_acc) + bonus_line_spiff
        else:
            val['comm'] = (mul_factor * month_acc)
        
        val['added'] = added_rev
        
        if is_bonus_spiff:
            val['spiff'] = (spiff_factor * month_acc) + bonus_handset_spiff
        else:
            val['spiff'] = (spiff_factor * month_acc)
        
        if phone_purchase != 'sim_only':
            if spiff_no_consider:
                if is_commission and is_added:
                    val['tot'] = val['comm'] + val['added']
                    val['spiff'] = 0.00
                elif is_commission:
                    val['tot'] = val['comm']
                    val['spiff'] = 0.00
                    val['added'] = 0.00
                elif is_added:
                    val['tot'] = val['added']
                    val['spiff'] = 0.00
                    vals['comm'] = 0.00
            else:
                if is_commission and is_spiff and is_added:
                    val['tot'] = val['comm'] + val['added'] + val['spiff']
                elif is_commission and is_spiff:
                    val['tot'] = val['comm'] + val['spiff']
                    val['added'] = 0
                elif is_commission and is_added:
                    val['tot'] = val['comm'] + val['added']
                    val['spiff'] = 0
                elif is_spiff and is_added:
                    val['tot'] = val['spiff'] + val['added']
                    val['comm'] = 0
                elif is_commission:
                    val['tot'] = val['comm']
                    val['spiff'] = 0
                    val['added'] = 0
                elif is_spiff:
                    val['tot'] = val['spiff']
                    val['comm'] = 0
                    val['added'] = 0
                elif is_added:
                    val['tot'] = val['added']
                    val['comm'] = 0
                    val['spiff'] = 0
        else:
            if is_commission and is_added:
                val['tot'] = val['comm'] + val['added']
                val['spiff'] = 0.00
            elif is_commission:
                val['tot'] = val['comm']
                val['spiff'] = 0
                val['added'] = 0
            elif is_added:
                val['tot'] = val['added']
                val['spiff'] = 0
                val['comm'] = 0
        return val

    def _calculate_postpaid_revenue_wrapper(self, cr, uid, ids, field_name, arg, context=None):
        return self._calculate_postpaid_revenue(cr, uid, ids, field_name, arg, context=context)

    def _calculate_postpaid_revenue(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        tac_record_ids = []
        spiff_no_consider = False
        line = self.browse(cr, uid, ids[0], context=context)
        revenue_obj = self.pool.get('revenue.generate.master')
        product_obj = self.pool.get('product.product')
        tac_obj = self.pool.get('tac.code.master')
        res[line.id] = {
                'dsr_rev_gen': 0.00,
                'dsr_comm_amnt':0.00,
                'dsr_comm_spiff':0.00,
                'dsr_comm_added':0.00,
                'dsr_comm_per_line':0.00
            }
        product_type = line.dsr_product_type.id
        credit_class_type = line.dsr_credit_class.category_type.id
        product = line.dsr_product_code.id
        prod_code_type = self.pool.get('product.product').browse(cr, uid, product).dsr_prod_code_type.id
        phone_purchase = line.dsr_phone_purchase_type
        dsr_id = line.product_id.id
        dsr_data = self.pool.get('wireless.dsr').browse(cr, uid, dsr_id)
        trans_date = dsr_data.dsr_date
        emp_des = dsr_data.dsr_designation_id.id
        line_no = line.dsr_line_no.id
        dsr_jod = line.dsr_jod
        imei = line.dsr_imei_no
        if imei:
            tac_record_ids = tac_obj.search(cr, uid, [('tac_code','=',imei[:8])])
        comm_percent = 0.00
        base_comm_obj = self.pool.get('comm.basic.commission.formula')
        base_comm_search = base_comm_obj.search(cr, uid, [('comm_designation','=',emp_des),('comm_start_date','<=',trans_date),('comm_end_date','>=',trans_date),('comm_inactive','=',False)])
        
        if base_comm_search:
            comm_percent = base_comm_obj.browse(cr, uid, base_comm_search[0]).comm_percent
        else:
            base_comm_search = base_comm_obj.search(cr, uid, [('comm_start_date','<=',trans_date),('comm_end_date','>=',trans_date),('comm_inactive','=',False)])
            if base_comm_search:
                comm_percent = base_comm_obj.browse(cr, uid, base_comm_search[0]).comm_percent
        
        rev_root_ids = revenue_obj.search(cr, uid, [('dsr_prod_type','=',product_type),('dsr_start_date','<=',trans_date),('dsr_end_date','>=',trans_date),('inactive','=',False)])
        if rev_root_ids:
            where_condition = []
            where_condition.append(('id','in',rev_root_ids))
            compare_string = str("")
            if len(rev_root_ids) == 1:
                compare_string += str("= %s"%(rev_root_ids[0]))
            else:
                compare_string += str("in %s"%(tuple(rev_root_ids),))
            cr.execute("select distinct(dsr_prod_code_type) from revenue_generate_master where id "+compare_string+"")
            master_prod_code_type = map(lambda x: x[0], cr.fetchall())
            cr.execute("select distinct(dsr_rev_product) from revenue_generate_master where id "+compare_string+"")
            master_product_ids = map(lambda x: x[0], cr.fetchall())
            cr.execute("select distinct(dsr_credit_class_type) from revenue_generate_master where id "+compare_string+"")
            master_class_type = map(lambda x: x[0], cr.fetchall())
            
            if prod_code_type in master_prod_code_type:
                where_condition.append(('dsr_prod_code_type','=',prod_code_type))
            if credit_class_type in master_class_type:
                where_condition.append(('dsr_credit_class_type','=',credit_class_type))
            if product in master_product_ids:
                where_condition.append(('dsr_rev_product','=',product))
            rev_final_ids = revenue_obj.search(cr, uid, where_condition)
            if rev_final_ids:
                compare_string = str("")
                if len(rev_final_ids) == 1:
                    compare_string += str("= %s"%(rev_final_ids[0]))
                else:
                    compare_string += str("in %s"%(tuple(rev_final_ids),))
                if tac_record_ids:
                    cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                            where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = false or rev.is_exclude is null)
                            and rev.dsr_jod = %s and tc.tac_id = %s''',(dsr_jod,tac_record_ids[0]))
                    revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                    if revenue_master_ids:
                        tac_ids = []
                        val = self._calculate_rev(cr, uid, revenue_master_ids[0], phone_purchase, product, line_no, spiff_no_consider)
                        res[line.id]['dsr_rev_gen'] = val['tot']
                        res[line.id]['dsr_comm_per_line'] = float(res[line.id]['dsr_rev_gen'] * comm_percent / 100)
                        res[line.id]['dsr_comm_amnt'] = val['comm']
                        res[line.id]['dsr_comm_added'] = val['added']
                        res[line.id]['dsr_comm_spiff'] = val['spiff']
                        return res
                cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                        where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = true or rev.is_exclude is null)
                        and rev.dsr_jod = %s''',(dsr_jod,))
                revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                if revenue_master_ids:
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(revenue_master_ids[0]))
                    tac_ids = map(lambda x: x[0], cr.fetchall())
                    for tac_record_each in tac_record_ids:
                        if tac_record_each in tac_ids:
                            spiff_no_consider = True
                    val = self._calculate_rev(cr, uid, revenue_master_ids[0], phone_purchase, product, line_no, spiff_no_consider)
                    res[line.id]['dsr_rev_gen'] = val['tot']
                    res[line.id]['dsr_comm_per_line'] = float(res[line.id]['dsr_rev_gen'] * comm_percent / 100)
                    res[line.id]['dsr_comm_amnt'] = val['comm']
                    res[line.id]['dsr_comm_added'] = val['added']
                    res[line.id]['dsr_comm_spiff'] = val['spiff']
                    return res                
                cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                        where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = true or rev.is_exclude is null)
                        and (rev.dsr_jod is null or rev.dsr_jod = false)''')
                revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                if revenue_master_ids:
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(revenue_master_ids[0]))
                    tac_ids = map(lambda x: x[0], cr.fetchall())
                    for tac_record_each in tac_record_ids:
                        if tac_record_each in tac_ids:
                            spiff_no_consider = True
                    val = self._calculate_rev(cr, uid, revenue_master_ids[0], phone_purchase, product, line_no,spiff_no_consider)
                    res[line.id]['dsr_rev_gen'] = val['tot']
                    res[line.id]['dsr_comm_per_line'] = float(res[line.id]['dsr_rev_gen'] * comm_percent / 100)
                    res[line.id]['dsr_comm_amnt'] = val['comm']
                    res[line.id]['dsr_comm_added'] = val['added']
                    res[line.id]['dsr_comm_spiff'] = val['spiff']
                    return res
                cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                        where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' 
                        and (rev.is_exclude = false or rev.is_exclude is null)
                        and (rev.dsr_jod is null or rev.dsr_jod = false)''')
                revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                if revenue_master_ids:
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(revenue_master_ids[0]))
                    tac_ids = map(lambda x: x[0], cr.fetchall())
                    for tac_record_each in tac_record_ids:
                        if tac_record_each not in tac_ids:
                            spiff_no_consider = True
                    val = self._calculate_rev(cr, uid, revenue_master_ids[0], phone_purchase, product, line_no, spiff_no_consider)
                    res[line.id]['dsr_rev_gen'] = val['tot']
                    res[line.id]['dsr_comm_per_line'] = float(res[line.id]['dsr_rev_gen'] * comm_percent / 100)
                    res[line.id]['dsr_comm_amnt'] = val['comm']
                    res[line.id]['dsr_comm_added'] = val['added']
                    res[line.id]['dsr_comm_spiff'] = val['spiff']
                    return res
            revenue_base_ids = revenue_obj.search(cr, uid, [('id','in',rev_final_ids),('is_exclude','=',False),('exclude_tac_code','=',False),('dsr_jod','=',False)])
            if revenue_base_ids:
                tac_ids = []
                val = self._calculate_rev(cr, uid, revenue_base_ids[0], phone_purchase, product, line_no, spiff_no_consider)
                res[line.id]['dsr_rev_gen'] = val['tot']
                res[line.id]['dsr_comm_per_line'] = float(res[line.id]['dsr_rev_gen'] * comm_percent / 100)
                res[line.id]['dsr_comm_amnt'] = val['comm']
                res[line.id]['dsr_comm_added'] = val['added']
                res[line.id]['dsr_comm_spiff'] = val['spiff']
                return res
        res[line.id]['dsr_rev_gen'] = 0.00
        res[line.id]['dsr_comm_per_line'] = 0.00
        res[line.id]['dsr_comm_amnt'] = 0.00
        res[line.id]['dsr_comm_spiff'] = 0.00
        res[line.id]['dsr_comm_added'] = 0.00
        return res


    def _calculate_data_rev(self, cr, uid, revenue_id, product, interval_type, phone_purchase, line_no, spiff_no_consider):
        #import ipdb;ipdb.set_trace()
        tac_master_ids = []
        is_commission = True
        is_spiff = True
        is_added = True
        is_bonus_comm = True
        is_bonus_spiff = True
        revenue_obj = self.pool.get('revenue.generate.master')
        product_obj = self.pool.get('product.product')
        tac_obj = self.pool.get('tac.code.master')
        mul_factor = revenue_obj.browse(cr, uid, revenue_id).dsr_revenue_calc
        spiff_factor = revenue_obj.browse(cr, uid, revenue_id).dsr_phone_spiff
        exclude_scnc = revenue_obj.browse(cr, uid, revenue_id).exclude_scnc
        added_rev = revenue_obj.browse(cr, uid, revenue_id).dsr_added_rev
        bonus_line_spiff = revenue_obj.browse(cr, uid, revenue_id).bonus_line_spiff
        bonus_handset_spiff = revenue_obj.browse(cr, uid, revenue_id).bonus_handset_spiff
        month_acc = product_obj.browse(cr, uid, product).monthly_access
        is_scnc = product_obj.browse(cr, uid, product).is_scnc
        if not line_no:
            line_no = 0
        cr.execute("select eligible_commission,eligible_spiff,eligible_added,eligible_bonus_comm,eligible_bonus_spiff from transaction_line_soc_rel where line_no = %s and (soc_code=%s or sub_soc_code=%s)"%(line_no,product,product))
        cal_data = cr.fetchall()
        for cal_data_each in cal_data:
            if cal_data_each:
                is_commission = cal_data_each[0]
                is_spiff = cal_data_each[1]
                is_added = cal_data_each[2]
                is_bonus_comm = cal_data_each[3]
                is_bonus_spiff = cal_data_each[4]
        val = val1 = tot = 0.00
        if is_bonus_comm:
            val = (mul_factor * month_acc) + bonus_line_spiff
        else:
            val = (mul_factor * month_acc)

        # if tac_ids and imei:
        #     for tac_id in tac_ids:
        #         if tac_id:
        #             tac_master_ids.append(tac_id[0])
        # if tac_master_ids and imei:
        #     for tac_data in tac_obj.browse(cr, uid, tac_master_ids):
        #         if imei[:8] == tac_data.tac_code:
        #             spiff_no_consider = True

        if exclude_scnc == True:            
            if interval_type == 'at_act' and is_scnc == False:
                if is_commission:
                    val = val
                if is_added:
                    val = val + added_rev
            else:
                if is_commission:
                    val = val
        else:
            if is_commission:
                val = val
            if is_added:
                val = val + added_rev
            
        #val1 = spiff_factor * month_acc#krishna code
        #tot = val + val1#krishna code
        
        #####shashank code 25/11#######s
        #import ipdb;ipdb.set_trace()
        if phone_purchase != 'sim_only':
            if is_bonus_spiff:
                val1 = (spiff_factor * month_acc) + bonus_handset_spiff
            else:
                val1 = (spiff_factor * month_acc)
        else:
            val1=0.0
        if spiff_no_consider:
            tot = val
        else:
            if is_spiff:
                tot = val + val1
            else:
                tot = val
        return tot

    def _calculate_data_feature_revenue(self, cr, uid, ids, product, product_type, prod_code_type, context=None):
        tac_record_ids = []
        line = self.browse(cr, uid, ids, context=context)
        spiff_no_consider = False
        revenue_obj = self.pool.get('revenue.generate.master')
        product_obj = self.pool.get('product.product')
        tac_obj = self.pool.get('tac.code.master')
        interval_type = 'at_act'
        credit_class_type = line.dsr_credit_class.category_type.id
        dsr_id = line.product_id.id
        line_no = line.dsr_line_no.id
        dsr_jod = line.dsr_jod
        imei = line.dsr_imei_no
        if imei:
            tac_record_ids = tac_obj.search(cr, uid, [('tac_code','=',imei[:8])])
        trans_date = self.pool.get('wireless.dsr').browse(cr, uid, dsr_id).dsr_date
        rev_root_ids = revenue_obj.search(cr, uid, [('dsr_prod_type','=',product_type),('dsr_start_date','<=',trans_date),('dsr_end_date','>=',trans_date),('inactive','=',False)])
        #import ipdb;ipdb.set_trace()
        phone_purchase = line.dsr_phone_purchase_type #alter by shashank on 25/11
        if rev_root_ids:
            where_condition = []
            where_condition.append(('id','in',rev_root_ids))
            compare_string = str("")
            if len(rev_root_ids) == 1:
                compare_string += str("= %s"%(rev_root_ids[0]))
            else:
                compare_string += str("in %s"%(tuple(rev_root_ids),))
            cr.execute("select distinct(dsr_activation_type) from revenue_generate_master where id "+compare_string+"")
            master_interval_type = map(lambda x: x[0], cr.fetchall())
            cr.execute("select distinct(dsr_prod_code_type) from revenue_generate_master where id "+compare_string+"")
            master_prod_code_type = map(lambda x: x[0], cr.fetchall())
            cr.execute("select distinct(dsr_rev_product) from revenue_generate_master where id "+compare_string+"")
            master_product_ids = map(lambda x: x[0], cr.fetchall())
            cr.execute("select distinct(dsr_credit_class_type) from revenue_generate_master where id "+compare_string+"")
            master_class_type = map(lambda x: x[0], cr.fetchall())
            
            if interval_type in master_interval_type:
                where_condition.append(('dsr_activation_type','=',interval_type))
            if prod_code_type in master_prod_code_type:
                where_condition.append(('dsr_prod_code_type','=',prod_code_type))
            if credit_class_type in master_class_type:
                where_condition.append(('dsr_credit_class_type','=',credit_class_type))
            if product in master_product_ids:
                where_condition.append(('dsr_rev_product','=',product))
            rev_final_ids = revenue_obj.search(cr, uid, where_condition)
            if rev_final_ids:
                compare_string = str("")
                if len(rev_final_ids) == 1:
                    compare_string += str("= %s"%(rev_final_ids[0]))
                else:
                    compare_string += str("in %s"%(tuple(rev_final_ids),))
                if tac_record_ids:
                    cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                            where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = false or rev.is_exclude is null)
                            and rev.dsr_jod = %s and tc.tac_id = %s''',(dsr_jod,tac_record_ids[0]))
                    revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                    if revenue_master_ids:
                        tac_ids = []
                        val = self._calculate_data_rev(cr, uid, revenue_master_ids[0], product, interval_type,phone_purchase, line_no, spiff_no_consider)
                        return val
                cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                        where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = true or rev.is_exclude is null)
                        and rev.dsr_jod = %s''',(dsr_jod,))
                revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                if revenue_master_ids:
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(revenue_master_ids[0]))
                    tac_ids = map(lambda x: x[0], cr.fetchall())
                    for tac_record_each in tac_record_ids:
                        if tac_record_each in tac_ids:
                            spiff_no_consider = True
                    val = self._calculate_data_rev(cr, uid, revenue_master_ids[0], product, interval_type,phone_purchase, line_no, spiff_no_consider)
                    return val
                cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                        where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = true or rev.is_exclude is null)
                        and (rev.dsr_jod is null or rev.dsr_jod = false)''')
                revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                if revenue_master_ids:
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(revenue_master_ids[0]))
                    tac_ids = map(lambda x: x[0], cr.fetchall())
                    for tac_record_each in tac_record_ids:
                        if tac_record_each in tac_ids:
                            spiff_no_consider = True
                    val = self._calculate_data_rev(cr, uid, revenue_master_ids[0], product, interval_type,phone_purchase, line_no, spiff_no_consider)
                    return val
                cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                        where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = false or rev.is_exclude is null)
                        and (rev.dsr_jod is null or rev.dsr_jod = false)''')
                revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                if revenue_master_ids:
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(revenue_master_ids[0]))
                    tac_ids = map(lambda x: x[0], cr.fetchall())
                    for tac_record_each in tac_record_ids:
                        if tac_record_each not in tac_ids:
                            spiff_no_consider = True
                    val = self._calculate_data_rev(cr, uid, revenue_master_ids[0], product, interval_type,phone_purchase, line_no, spiff_no_consider)
                    return val
            revenue_base_ids = revenue_obj.search(cr, uid, [('id','in',rev_final_ids),('is_exclude','=',False),('exclude_tac_code','=',False),('dsr_jod','=',False)])
            if revenue_base_ids:
                tac_ids = []
                val = self._calculate_data_rev(cr, uid, revenue_base_ids[0], product, interval_type,phone_purchase, line_no, spiff_no_consider)
                return val
        val = 0
        return val

    def _calculate_revenue_pos(self, cr, uid, ids, field_name, arg, context=None):
        tac_record_ids = []
        line = self.browse(cr, uid, ids, context=context)
        spiff_no_consider = False
        #import ipdb;ipdb.set_trace()
        revenue_obj = self.pool.get('revenue.generate.master')
        product_obj = self.pool.get('product.product')
        credit_obj = self.pool.get('credit.class')
        tac_obj = self.pool.get('tac.code.master')
        product_type = line.dsr_product_type.id
        credit_class_type = line.dsr_credit_class.category_type.id
        dsr_jod = line.dsr_jod
        imei = line.dsr_imei_no
        if imei:
            tac_record_ids = tac_obj.search(cr, uid, [('tac_code','=',imei[:8])])
        line_no = line.dsr_line_no.id
        product = line.dsr_product_code.id
        prod_code_type = self.pool.get('product.product').browse(cr, uid, product).dsr_prod_code_type.id
        phone_purchase = line.dsr_phone_purchase_type
        cr.execute("select product_id from wireless_dsr_postpaid_line where id=%s"%(line.id,))
        dsr_data_id = cr.fetchall()
        dsr_id = dsr_data_id[0][0]
        trans_date = self.pool.get('wireless.dsr').browse(cr, uid, dsr_id).dsr_date
        rev_root_ids = revenue_obj.search(cr, uid, [('dsr_prod_type','=',product_type),('dsr_start_date','<=',trans_date),('dsr_end_date','>=',trans_date),('inactive','=',False)])
        if rev_root_ids:
            where_condition = []
            where_condition.append(('id','in',rev_root_ids))
            compare_string = str("")
            if len(rev_root_ids) == 1:
                compare_string += str("= %s"%(rev_root_ids[0]))
            else:
                compare_string += str("in %s"%(tuple(rev_root_ids),))
            cr.execute("select distinct(dsr_prod_code_type) from revenue_generate_master where id "+compare_string+"")
            master_prod_code_type = map(lambda x: x[0], cr.fetchall())
            cr.execute("select distinct(dsr_rev_product) from revenue_generate_master where id "+compare_string+"")
            master_product_ids = map(lambda x: x[0], cr.fetchall())
            cr.execute("select distinct(dsr_credit_class_type) from revenue_generate_master where id "+compare_string+"")
            master_class_type = map(lambda x: x[0], cr.fetchall())
            
            if prod_code_type in master_prod_code_type:
                where_condition.append(('dsr_prod_code_type','=',prod_code_type))
            if credit_class_type in master_class_type:
                where_condition.append(('dsr_credit_class_type','=',credit_class_type))
            if product in master_product_ids:
                where_condition.append(('dsr_rev_product','=',product))
            
            rev_final_ids = revenue_obj.search(cr, uid, where_condition)
            if rev_final_ids:
                compare_string = str("")
                if len(rev_final_ids) == 1:
                    compare_string += str("= %s"%(rev_final_ids[0]))
                else:
                    compare_string += str("in %s"%(tuple(rev_final_ids),))
                if tac_record_ids:
                    cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                            where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = false or rev.is_exclude is null)
                            and rev.dsr_jod = %s and tc.tac_id = %s''',(dsr_jod,tac_record_ids[0]))
                    revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                    if revenue_master_ids:
                        tac_ids = []
                        val = self._calculate_rev(cr, uid, revenue_master_ids[0], phone_purchase, product, line_no, spiff_no_consider)
                        return val
                cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                        where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = true or rev.is_exclude is null)
                        and rev.dsr_jod = %s''',(dsr_jod,))
                revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                if revenue_master_ids:
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(revenue_master_ids[0]))
                    tac_ids = map(lambda x: x[0], cr.fetchall())
                    for tac_record_each in tac_record_ids:
                        if tac_record_each in tac_ids:
                            spiff_no_consider = True
                    val = self._calculate_rev(cr, uid, revenue_master_ids[0], phone_purchase, product, line_no, spiff_no_consider)
                    return val
                cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                        where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = true or rev.is_exclude is null)
                        and (rev.dsr_jod is null or rev.dsr_jod = false)''')
                revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                if revenue_master_ids:
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(revenue_master_ids[0]))
                    tac_ids = map(lambda x: x[0], cr.fetchall())
                    for tac_record_each in tac_record_ids:
                        if tac_record_each in tac_ids:
                            spiff_no_consider = True
                    val = self._calculate_rev(cr, uid, revenue_master_ids[0], phone_purchase, product, line_no, spiff_no_consider)
                    return val
                cr.execute('''select rev.id from revenue_generate_master rev, rev_formula_master_tac_rel tc
                        where tc.rev_formula_id = rev.id and rev.id '''+compare_string+''' and (rev.is_exclude = false or rev.is_exclude is null)
                        and (rev.dsr_jod is null or rev.dsr_jod = false)''')
                revenue_master_ids = map(lambda x: x[0], cr.fetchall())
                if revenue_master_ids:
                    cr.execute("select tac_id from rev_formula_master_tac_rel where rev_formula_id = %s"%(revenue_master_ids[0]))
                    tac_ids = map(lambda x: x[0], cr.fetchall())
                    for tac_record_each in tac_record_ids:
                        if tac_record_each not in tac_ids:
                            spiff_no_consider = True
                    val = self._calculate_rev(cr, uid, revenue_master_ids[0], phone_purchase, product, line_no, spiff_no_consider)
                    return val
            revenue_base_ids = revenue_obj.search(cr, uid, [('id','in',rev_final_ids),('is_exclude','=',False),('exclude_tac_code','=',False),('dsr_jod','=',False)])
            if revenue_base_ids:
                tac_ids = []
                val = self._calculate_rev(cr, uid, revenue_base_ids[0], phone_purchase, product, line_no, spiff_no_consider)
                return val
        val = 0
        return val

    def _calculate_total_postpaid_rev(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            revenue_obj = self.pool.get('revenue.generate.master')
            product_obj = self.pool.get('product.product')
            dsr_id = line.product_id.id
            dsr_data = self.pool.get('wireless.dsr').browse(cr, uid, dsr_id)
            trans_date = dsr_data.dsr_date
            emp_des = dsr_data.dsr_designation_id.id
            comm_percent = 0.00
#            base_comm_obj = self.pool.get('comm.basic.commission.formula')
#            base_comm_search = base_comm_obj.search(cr, uid, [('comm_designation','=',emp_des),('comm_start_date','<=',trans_date),('comm_end_date','>=',trans_date),('comm_inactive','=',False)])
#            if base_comm_search:
#                comm_percent = base_comm_obj.browse(cr, uid, base_comm_search[0]).comm_percent
#            else:
#                base_comm_search = base_comm_obj.search(cr, uid, [('comm_start_date','<=',trans_date),('comm_end_date','>=',trans_date),('comm_inactive','=',False)])
#                if base_comm_search:
#                    comm_percent = base_comm_obj.browse(cr, uid, base_comm_search[0]).comm_percent
            res[line.id] = {
                            'dsr_tot_rev_gen':0.00,
                            'dsr_tot_comm_per_line':0.00
                            }
            val = 0.00
            # val2 = self._calculate_postpaid_revenue(cr, uid, ids, field_name, arg, context=context)
            # val1 = val2[line.id]['dsr_rev_gen']
            # val = val + val1
            product = line.dsr_product_code.id
            prod_data = product_obj.browse(cr, uid, product)
            product_type = prod_data.categ_id.id
            prod_code_type = prod_data.dsr_prod_code_type.id
            val1 = self._calculate_revenue_pos(cr, uid, line.id, field_name, arg, context=context)
            if val1:
                val = val + val1['tot']
            if line.jump == True:
                jump_soc = line.jump_soc.id
                jump_prod_type = line.jump_soc.categ_id.id
                jump_prod_code_type = line.jump_soc.dsr_prod_code_type.id
                val1 = self._calculate_data_feature_revenue(cr, uid, line.id, jump_soc, jump_prod_type, jump_prod_code_type)
                val = val + val1
            if line.intl_feature == True:
                intl_soc = line.intl_feature_soc.id
                intl_prod_type = line.intl_feature_soc.categ_id.id
                intl_prod_code_type = line.intl_feature_soc.dsr_prod_code_type.id
                val1 = self._calculate_data_feature_revenue(cr, uid, line.id, intl_soc, intl_prod_type, intl_prod_code_type)
                val = val + val1
            if line.data == True:
                data_soc = line.data_soc.id
                data_prod_type = line.data_soc.categ_id.id
                data_prod_code_type = line.data_soc.dsr_prod_code_type.id
                val1 = self._calculate_data_feature_revenue(cr, uid, line.id, data_soc, data_prod_type, data_prod_code_type)
                val = val + val1
            if line.other == True:
                other_soc = line.other_soc.id
                other_prod_type = line.other_soc.categ_id.id
                other_prod_code_type = line.other_soc.dsr_prod_code_type.id
                val1 = self._calculate_data_feature_revenue(cr, uid, line.id, other_soc, other_prod_type, other_prod_code_type)
                val = val + val1
            #import ipdb;ipdb.set_trace()
            res[line.id]['dsr_tot_rev_gen'] = val
            res[line.id]['dsr_tot_comm_per_line'] = float(val * comm_percent / 100)
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('wireless.dsr.postpaid.line').browse(cr, uid, ids, context=context):
            result[line.id] = True
        return result.keys()

    _columns = {
                'product_id':fields.many2one('wireless.dsr','Product Id'),
                'dsr_trans_type':fields.selection(_prod_type, 'Transaction Type'),
                # 'creation_date':fields.date('Create Date'),
                'dsr_product_type':fields.many2one('product.category','Product Type'),
                ### below product Code type added for testing benefit
                'dsr_product_code_type':fields.many2one('product.category','Product Code Type'),
                # 'dsr_product_code_type':fields.char('Product Code Type', size=64),
                'dsr_product_code':fields.many2one('product.product', 'Product Code'),
                'dsr_line_no':fields.many2one('credit.line.limit','Line #'),
                'is_voice':fields.boolean('Voice Barred'),
                'is_mobile':fields.boolean('Mobile Internet'),
                'is_jump':fields.boolean('JUMP Attached'),
                # 'dsr_product_description':fields.char('Product Description', size=64),
                'act_type':fields.selection([('Act','Activation'),('reactivation','Reactivation'),('deactivation','DeActivation')], 'Activation Type'),
                'dsr_credit_class':fields.many2one('credit.class', 'Credit class'),
                'dsr_credit_class_type':fields.many2one('credit.class.type', 'Credit Class Type'),
                'is_emp_upg':fields.boolean('Employee Upgrade'),
                'dsr_p_number':fields.char('P-number'),
                'dsr_emp_type':fields.many2one('dsr.employee.type','T-Mobile Employee'),
                # 'dsr_activiation_interval':fields.many2one('dsr.activation.interval.type','Activation Interval'),
                'dsr_phone_no':fields.char('Mobile Phone', size=10),
                'dsr_mob_port':fields.boolean('Mobile # Port'),
                'dsr_port_comp':fields.many2one('port.company', 'Port Company'),
                'dsr_temp_no':fields.char('Temporary #', size=10),
                'dsr_cust_ban_no':fields.char('BAN no.', size=16),
                'dsr_sim_no': fields.char('SIM #', size=25),
                'dsr_ship_to':fields.boolean('Ship To'),
                # 'dsr_dummy_imei':fields.char('Dummy IMEI #', size=15, help="You need to enter reason in DSR Notes for Dummy IMEI"),
                'dsr_imei_no':fields.char('IMEI #', size=15),
                'dsr_eip_no':fields.char('EIP #', size=16),
                # 'dsr_warranty':fields.char('Warranty Exchange Order #', size=16),
                'jump':fields.boolean('JUMP or PHP'),
                'intl_feature':fields.boolean('International Feature'),
                'data':fields.boolean('Data'),
                # 'messaging':fields.boolean('Messaging'),
                'other':fields.boolean('Other'),
                'jump_soc':fields.many2one('product.product','JUMP or PHP SOC code'),
                'intl_feature_soc':fields.many2one('product.product','International Feature SOC code'),
                'data_soc':fields.many2one('product.product','Data SOC code'),
                # 'msg_soc':fields.many2one('product.product','Messaging SOC code'),
                'other_soc':fields.many2one('product.product','Other SOC code'),
                'dsr_act_date':fields.date('Activation Date'),
                'pseudo_date':fields.date('Pseudo Transaction Date'),
                'dsr_deact_date':fields.date('DeActivation Date'),
                'act_recon':fields.boolean('Act Reconciled'),
                'deact_recon':fields.boolean('DeAct Reconciled'),
                'state':fields.selection([('draft','Draft'),('pending','Pending'),('cancel','Cancel'),('done','Done'),('void','VOID')],'Status', readonly=True),
                'dsr_phone_purchase_type':fields.selection([('new_device','EIP'),('sim_only','SIM Only'),('device_outright','Device Outright')],'Phone Purchased'),
                'dsr_react_date':fields.date('ReActivation Date'),
                'react_recon':fields.boolean('ReAct Reconciled'),
                'dsr_trade_inn':fields.selection([('yes','Yes'),('no','No')],'Trade-in'),
                # 'state_postpaid':fields.related('product_id', 'state', type='selection', string="State", relation='wireless.dsr',store=True),
                'dsr_rev_gen':fields.function(_calculate_postpaid_revenue_wrapper, string="Total Amount", type='float', multi='sums',
                        store={
                                'wireless.dsr.postpaid.line': (_get_order, [], 10),
                }),
                'dsr_comm_amnt':fields.function(_calculate_postpaid_revenue_wrapper, string="DSR Commission Amount", type='float', multi='sums',
                        store={
                                'wireless.dsr.postpaid.line': (_get_order, [], 10),
                }),
                'dsr_comm_spiff':fields.function(_calculate_postpaid_revenue_wrapper, string="DSR Spiff Amount", type='float', multi='sums',
                        store={
                                'wireless.dsr.postpaid.line': (_get_order, [], 10),
                }),
                'dsr_comm_added':fields.function(_calculate_postpaid_revenue_wrapper, string="DSR Added Amount", type='float', multi='sums',
                        store={
                                'wireless.dsr.postpaid.line': (_get_order, [], 10),
                }),
                'dsr_comm_per_line':fields.function(_calculate_postpaid_revenue_wrapper, string="Commission per line", type='float', multi='sums',
                    store={
                                'wireless.dsr.postpaid.line': (_get_order, [], 10),
                }),
                'dsr_tot_comm_per_line':fields.function(_calculate_total_postpaid_rev, string="Total Commission per line", type='float', multi='sums'),
                'dsr_tot_rev_gen':fields.function(_calculate_total_postpaid_rev, string="Total Rev Gen.", type="float", multi='sums'),
                'dsr_rev_gen_exp':fields.float('Export Rev Gen'),
                'dsr_comm_amnt_exp':fields.float('Export Commission'),
                'dsr_comm_spiff_exp':fields.float('Export Spiff'),
                'dsr_comm_added_exp':fields.float('Export Added Rev'),
                'dsr_tot_rev_gen_exp':fields.float('Export Total Rev Gen'),
                'valid': fields.many2one('crashing.validation.flag','Valid'),
                'dsr_jod':fields.boolean('JUMP on Demand'),
                'dsr_smd':fields.boolean('SMD'),
                'dsr_contract_term':fields.integer('Contract Term'),
                'dsr_monthly_access':fields.float('Monthle Access'),
                'pmd': fields.char('PMD Name',size=890),
                'is_commission_cr': fields.boolean('Carrier'),
                'spiff_amt': fields.float('Spiff Amt'),
                'commission_amt': fields.float('Commissions Amt'),
                # 'dsr_act_date_new': fields.date('Activation Date New'),
                # 'dsr_deact_date_new': fields.date('Deactivation Date New'),
                # 'dsr_react_date_new': fields.date('Reactivation Date New'),
                'crash_act_date': fields.date('Crashing Activation Date'),
                'crash_deact_date': fields.date('Crashing Deactivation Date'),
                'crash_react_date': fields.date('Crashing Reactivation Date'),
                'comments': fields.text('Reasons For Deactivation of Chargebacks'),
                'noncommissionable':fields.boolean('Non Commissionable'),
                'dsr_pmd': fields.boolean('PMD'),
                'employee_id' : fields.many2one('hr.employee','Emp'),
                'store_id':fields.many2one('sap.store', 'Store'),
                'market_id':fields.many2one('market.place', 'Market'),
                'region_id':fields.many2one('market.regions', 'Region'),
                # 'dsr_crash_activation': fields.many2one('dsr.tmob.crash.process','Activation'),
                # 'dsr_crash_deactivation': fields.many2one('dsr.crash.process.deactivation','Deactivation'),
                'eip_phone_purchase':fields.boolean('EIP Phone Purchased'),
                'dsr_jump_already':fields.boolean('JUMP already on Account'),
                'dsr_phone_first':fields.many2one('phone.type.master', 'Device Type'),
                'dsr_transaction_id':fields.char('Transaction ID', size=64),
                'customer_name':fields.char('customer name', size=64),
                'dealer_code':fields.char('Dealer Code', size=1024),
                'dsr_exception':fields.boolean('Exception'),
                'dsr_designation_id':fields.many2one('hr.job','Designation')
                #'tmob_comments' : fields.text('Tmobile Comments'),#### field added as per the change to update the T-mobile comments
                #'valid_neutral': fields.many2one('crashing.validation.flag','Valid Non-Zero'),#### field added to be used for nonzero crash
    }
    _defaults = {
                'state':'draft',
                'act_type':'Act',
                'dsr_trans_type':'postpaid',
                'dsr_exception':False,
                'is_jump':False
    }

    def onchange_credit_class(self, cr, uid, ids, dsr_credit_class, product_type):
        cc_obj = self.pool.get('credit.class')
        emp_type_obj = self.pool.get('dsr.employee.type')
        is_emp_upg = False
        dsr_emp_type = False
        vals = {
                'dsr_credit_class_type':False,
                'dsr_product_code':False,
                'is_emp_upg':False,
                'dsr_emp_type':False,
                'dsr_p_number':False,
                'dsr_product_type':product_type
            }            
        domain = {'dsr_product_code':[('categ_id','=',product_type)]}
        if dsr_credit_class and product_type:
            cc_data = cc_obj.browse(cr, uid, dsr_credit_class)
            cc_type = cc_data.category_type.id
            is_scnc = cc_data.is_scnc
            cc_prod_type = cc_data.prod_type.id
            if cc_data.is_emp_upg:
                is_emp_upg = True
                emp_ids = emp_type_obj.search(cr, uid, [('is_emp_upg','=',is_emp_upg)])
                if emp_ids:
                    dsr_emp_type = emp_ids[0]
            if is_scnc:
                domain = {'dsr_product_code':[('is_scnc','=',True),('categ_id','=',product_type)]}
            else:
                domain = {'dsr_product_code':[('categ_id','=',product_type),('is_scnc','=',False)]}
            vals = {
                    'dsr_credit_class_type':cc_type,
                    'dsr_product_code':False,
                    'is_emp_upg':is_emp_upg,
                    'dsr_emp_type':dsr_emp_type,
                    'dsr_p_number':False,
                    'dsr_product_type':product_type
            }
            cc_ids = cc_obj.search(cr, uid, [('prod_type','=',product_type)])
            cc_ids2 = cc_obj.search(cr, uid, [('prod_type','=',False)])
            if cc_ids and (dsr_credit_class not in cc_ids):
                vals['dsr_product_type'] = False
            elif (not cc_ids) and cc_ids2 and (dsr_credit_class not in cc_ids2):
                vals['dsr_product_type'] = False
            return {'value':vals,'domain':domain}
        return {'value':vals,'domain':domain}

    def onchange_phone_purchase(self, cr, uid, ids, phone_purchase, dsr_jod):
        vals = {                
                'dsr_eip_no':False,
                'dsr_trade_inn':False,
                'dsr_jod':False
        }
        domain = {'jump_soc':[]}
        if phone_purchase:
            if phone_purchase == 'sim_only':
                vals = {
                        'dsr_eip_no':False,
                        'dsr_trade_inn':False,
                        'jump':False,
                        'jump_soc':False,
                        'other':False,
                        'other_soc':False,
                        'dsr_jod':False
                }
                domain = {
                         'jump_soc':['|',('is_php','=',True),('is_jump','=',True),('dsr_categ_id','=','feature')]
                }
            elif phone_purchase == 'device_outright':
                vals = {
                        'dsr_eip_no':False,
                        'dsr_trade_inn':False,
                        'jump':False,
                        'other':False,
                        'jump_soc':False,
                        'other_soc':False,
                        'dsr_jod':False
                }
                domain = {
                        'jump_soc':[('is_php','=',True),('dsr_categ_id','=','feature')]
                }
            elif phone_purchase == 'new_device':
                vals = {
                        'jump':False,
                        'jump_soc':False,
                        'other':False,
                        'other_soc':False
                }
                if dsr_jod:
                    domain = {
                            'jump_soc':[('is_php','=',True),('dsr_categ_id','=','feature')]
                            }
                else:
                    domain = {
                            'jump_soc':['|',('is_php','=',True),('is_jump','=',True),('dsr_categ_id','=','feature')]
                            }
            return {'value':vals,'domain':domain}
        return {'value':vals}

    def onchange_mob_port(self, cr, uid, ids, mob_port):
        if not mob_port:
            return {'value':{'dsr_port_comp':False,'dsr_temp_no':False}}
        return {}

    def onchange_product_type(self, cr, uid, ids, product_type):
        cc_obj = self.pool.get('credit.class')
        if product_type:
            cc_ids = cc_obj.search(cr, uid, [('prod_type','=',product_type)])
            if cc_ids:
                domain = {'dsr_credit_class':[('prod_type','=',product_type)],'dsr_product_code':[('categ_id','=',product_type)]}
            else:
                domain = {'dsr_credit_class':[('prod_type','=',False)],'dsr_product_code':[('categ_id','=',product_type)]}
            return {'value': {'dsr_product_code' : False,'dsr_credit_class':False},'domain':domain}
        domain = {'dsr_credit_class':[],'dsr_product_code':[('categ_id','=',False)]}
        return {'value':{'dsr_product_code':False,'dsr_credit_class':False},'domain':domain}

    def onchange_soc(self, cr, uid, ids, dsr_product_code, credit_class):
        vals = {}
        domain = {
                'data_soc':[('is_data','=',True),('dsr_categ_id','=','feature')]
        }
        prod_obj = self.pool.get('product.product')
        prod_rule = self.pool.get('product.business.rule')
        cc_obj = self.pool.get('credit.class')
        if dsr_product_code:
            pr_data = prod_obj.browse(cr, uid, dsr_product_code)
            prod_code_type = pr_data.dsr_prod_code_type.id
            prod_type = pr_data.categ_id.id
            monthly_access = pr_data.monthly_access
            contract_term = pr_data.contract_term
            vals = {'dsr_product_code_type':prod_code_type,
                    'dsr_monthly_access':monthly_access,
                    'dsr_contract_term':contract_term,
                    'data':False,
                    'data_soc':False
                    }
            is_scnc = pr_data.is_scnc
            cr.execute("select data_soc_id from product_business_rule where main_soc_id = %s and active = true"%(dsr_product_code))
            prod_rule_ids = map(lambda x: x[0], cr.fetchall())
            domain['data_soc'] += [('id','in',prod_rule_ids)]
            if credit_class:
                cc_scnc = cc_obj.browse(cr, uid, credit_class).is_scnc
                if cc_scnc != is_scnc:
                    vals.update({'dsr_credit_class':False})
            return {'value':vals,'domain':domain}
        vals = {
                'dsr_product_code_type':False,
                'dsr_monthly_access':False,
                'dsr_contract_term':False,
                'data_soc':False,
                'data':False
        }
        return {'value':vals,'domain':domain}
    
    def onchange_data_soc(self, cr, uid, ids, data_soc, main_prod):
        vals = {}
        if main_prod and data_soc:
            cr.execute("select main_soc_id from product_business_rule where data_soc_id = %s and active = true"%(data_soc,))
            product_search_ids = map(lambda x: x[0], cr.fetchall())
            if main_prod not in product_search_ids:
                vals = {'dsr_product_code':False}
            return {'value':vals}
        return {}

    def onchange_jump(self, cr, uid, ids, jump):
        if not jump:
            return {'value':{'jump_soc':False}}
        return {}

    def onchange_jump_soc(self, cr, uid, ids, jump_soc):
        prod_obj = self.pool.get('product.product')
        if jump_soc:
            jump = prod_obj.browse(cr, uid, jump_soc).is_jump
            return {'value':{'is_jump':jump}}
        return {'value':{'is_jump':False}}

    def onchange_data(self, cr, uid, ids, data):
        if not data:
            return {'value':{'data_soc':False}}
        return {}

    def onchange_intl_feature(self, cr, uid, ids, intl_feature):
        if not intl_feature:
            return {'value':{'intl_feature_soc':False}}
        return {}

    def onchange_other(self, cr, uid, ids, other):
        if not other:
            return {'value':{'other_soc':False}}
        return {}

    def onchange_phone(self, cr, uid, ids, phone):
        if phone:
            phone_check(phone)
            return {}
        return {}

    def onchange_sim(self, cr, uid, ids, sim):
        if sim:
            sim_validation(sim)
            return {}
        return {}

    def onchange_imei(self, cr, uid, ids, imei, dsr_phone_purchase_type):
        if imei and dsr_phone_purchase_type:
            if dsr_phone_purchase_type != 'sim_only':
                imei_check(imei)
            return {}
        return {}

    def onchange_temp(self, cr, uid, ids, temp):
        if temp:
            temp_check(temp)
            return {}
        return {}

    def _create_data_feature(self, cr, uid, vals, res):
        prod_obj = self.pool.get('product.product')
        cc_obj = self.pool.get('credit.class')
        cc_data_browse = cc_obj.browse(cr, uid, vals['dsr_credit_class'])
        if vals['jump'] and vals['jump_soc']:
            prod_jump_browse = prod_obj.browse(cr, uid, vals['jump_soc'])
            jump_data = {   'dsr_product_code' : vals['jump_soc'],
                            'feature_product_id':vals['product_id'],
                            'dsr_product_type':prod_jump_browse.categ_id.id,
                            'dsr_eip_no':vals['dsr_eip_no'],
                            # 'dsr_warranty':vals['dsr_warranty'],
                            'dsr_jump':True,
                            'dsr_product_code_type' : prod_jump_browse.dsr_prod_code_type.id,
                            'dsr_monthly_access':prod_jump_browse.monthly_access,
                            'dsr_contract_term':prod_jump_browse.contract_term,
                            # 'dsr_product_description' : prod_jump_browse.name,
                            'dsr_phone_no' : vals['dsr_phone_no'],
                            'dsr_cust_ban_no' : vals['dsr_cust_ban_no'],
                            'dsr_sim_no' : vals['dsr_sim_no'],
                            'dsr_imei_no' : vals['dsr_imei_no'],
                            'dsr_credit_class' : vals['dsr_credit_class'],
                            'is_emp_upg':vals['is_emp_upg'],
                            'dsr_emp_type':vals['dsr_emp_type'],
                            'dsr_p_number':vals['dsr_p_number'],
                            'dsr_line_no':vals.get('dsr_line_no'),
                            'dsr_jod':vals.get('dsr_jod'),
                            # 'dsr_credit_class_type' : cc_data_browse.category_type.id,
                            'dsr_activiation_interval' : 'at_act',
                            'postpaid_id' : res,
                            'dsr_temp_no':vals['dsr_temp_no'],
                            'dsr_phone_purchase_type':vals['dsr_phone_purchase_type'],
                            'dsr_trade_inn':vals['dsr_trade_inn'],
                            'dsr_mob_port':vals['dsr_mob_port'],
                            'dsr_port_comp':vals['dsr_port_comp'],
                            'dsr_ship_to':vals['dsr_ship_to']
                        }
            self.pool.get('wireless.dsr.feature.line').create(cr, uid, jump_data)
        if vals['data'] and vals['data_soc']:
            prod_data_browse = prod_obj.browse(cr, uid, vals['data_soc'])
            data = {        'dsr_product_code' : vals['data_soc'],
                            'feature_product_id':vals['product_id'],
                            'dsr_product_type':prod_data_browse.categ_id.id,
                            'dsr_product_code_type' : prod_data_browse.dsr_prod_code_type.id,
                            'dsr_monthly_access':prod_data_browse.monthly_access,
                            'dsr_contract_term':prod_data_browse.contract_term,
                            # 'dsr_product_description' : prod_data_browse.name,
                            'dsr_eip_no':vals['dsr_eip_no'],
                            'dsr_phone_no' : vals['dsr_phone_no'],
                            'dsr_cust_ban_no' : vals['dsr_cust_ban_no'],
                            'dsr_sim_no' : vals['dsr_sim_no'],
                            'dsr_imei_no' : vals['dsr_imei_no'],
                            'dsr_credit_class' : vals['dsr_credit_class'],
                            'is_emp_upg':vals['is_emp_upg'],
                            'dsr_emp_type':vals['dsr_emp_type'],
                            'dsr_p_number':vals['dsr_p_number'],
                            'dsr_line_no':vals.get('dsr_line_no'),
                            'dsr_jod':vals.get('dsr_jod'),
                            # 'dsr_credit_class_type' : cc_data_browse.category_type.id,
                            'dsr_activiation_interval' : 'at_act',
                            'postpaid_id' : res,
                            'dsr_temp_no':vals['dsr_temp_no'],
                            'dsr_phone_purchase_type':vals['dsr_phone_purchase_type'],
                            'dsr_trade_inn':vals['dsr_trade_inn'],
                            'dsr_mob_port':vals['dsr_mob_port'],
                            'dsr_port_comp':vals['dsr_port_comp'],
                            'dsr_ship_to':vals['dsr_ship_to']
                    }
            self.pool.get('wireless.dsr.feature.line').create(cr, uid, data)
        if vals['intl_feature'] and vals['intl_feature_soc']:
            prod_intl_feature_browse = prod_obj.browse(cr, uid, vals['intl_feature_soc'])
            intl_feature_data = {'dsr_product_code' : vals['intl_feature_soc'],
                                'feature_product_id':vals['product_id'],
                                'dsr_product_type':prod_intl_feature_browse.categ_id.id,
                                'dsr_product_code_type' : prod_intl_feature_browse.dsr_prod_code_type.id,
                                'dsr_monthly_access':prod_intl_feature_browse.monthly_access,
                                'dsr_contract_term':prod_intl_feature_browse.contract_term,
                                # 'dsr_product_description' : prod_intl_feature_browse.name,
                                'dsr_eip_no':vals['dsr_eip_no'],
                                'dsr_phone_no' : vals['dsr_phone_no'],
                                'dsr_cust_ban_no' : vals['dsr_cust_ban_no'],
                                'dsr_sim_no' : vals['dsr_sim_no'],
                                'dsr_imei_no' : vals['dsr_imei_no'],
                                'dsr_credit_class' : vals['dsr_credit_class'],
                                'is_emp_upg':vals['is_emp_upg'],
                                'dsr_emp_type':vals['dsr_emp_type'],
                                'dsr_p_number':vals['dsr_p_number'],
                                'dsr_line_no':vals.get('dsr_line_no'),
                                'dsr_jod':vals.get('dsr_jod'),
                                # 'dsr_credit_class_type' : cc_data_browse.category_type.id,
                                'dsr_activiation_interval' : 'at_act',
                                'postpaid_id' : res,
                                'dsr_temp_no':vals['dsr_temp_no'],
                                'dsr_phone_purchase_type':vals['dsr_phone_purchase_type'],
                                'dsr_trade_inn':vals['dsr_trade_inn'],
                                'dsr_mob_port':vals['dsr_mob_port'],
                                'dsr_port_comp':vals['dsr_port_comp'],
                                'dsr_ship_to':vals['dsr_ship_to']
                            }
            self.pool.get('wireless.dsr.feature.line').create(cr, uid, intl_feature_data)
        if vals['other'] and vals['other_soc']:
            prod_other_browse = prod_obj.browse(cr, uid, vals['other_soc'])
            other_data = {  'dsr_product_code' : vals['other_soc'],
                            'feature_product_id':vals['product_id'],
                            'dsr_product_type':prod_other_browse.categ_id.id,
                            'dsr_product_code_type' : prod_other_browse.dsr_prod_code_type.id,
                            'dsr_monthly_access':prod_other_browse.monthly_access,
                            'dsr_contract_term':prod_other_browse.contract_term,
                            # 'dsr_product_description' : prod_other_browse.name,
                            'dsr_eip_no':vals['dsr_eip_no'],
                            'dsr_phone_no' : vals['dsr_phone_no'],
                            'dsr_cust_ban_no' : vals['dsr_cust_ban_no'],
                            'dsr_sim_no' : vals['dsr_sim_no'],
                            'dsr_imei_no' : vals['dsr_imei_no'],
                            'dsr_credit_class' : vals['dsr_credit_class'],
                            'is_emp_upg':vals['is_emp_upg'],
                            'dsr_emp_type':vals['dsr_emp_type'],
                            'dsr_p_number':vals['dsr_p_number'],
                            'dsr_line_no':vals.get('dsr_line_no'),
                            'dsr_jod':vals.get('dsr_jod'),
                            # 'dsr_credit_class_type' : cc_data_browse.category_type.id,
                            'dsr_activiation_interval' : 'at_act',
                            'postpaid_id' : res,
                            'dsr_temp_no':vals['dsr_temp_no'],
                            'dsr_phone_purchase_type':vals['dsr_phone_purchase_type'],
                            'dsr_trade_inn':vals['dsr_trade_inn'],
                            'dsr_mob_port':vals['dsr_mob_port'],
                            'dsr_port_comp':vals['dsr_port_comp'],
                            'dsr_ship_to':vals['dsr_ship_to']
                            }
            self.pool.get('wireless.dsr.feature.line').create(cr, uid, other_data)
        return True

    def check_jump_score_php(self, cr, uid, phone_purchase, jump_soc, other_soc, dsr_jod):
        prod_obj = self.pool.get('product.product')
        jump_soc = prod_obj.browse(cr, uid, jump_soc)
        other_soc = prod_obj.browse(cr, uid, other_soc)
        if phone_purchase == 'new_device':
            if jump_soc and other_soc:
                if other_soc.is_score:
                    raise osv.except_osv(('Warning!!'),('You can have only JUMP/PHP or Score attached with EIP phone purchase type in Postpaid Line.'))
            if dsr_jod and jump_soc.is_jump:
                raise osv.except_osv(('Warning!!'),('You cannot have JUMP attached, if JUMP on Demand is selected.'))
        elif phone_purchase == 'device_outright':
            if jump_soc and other_soc:
                if other_soc.is_score:
                    raise osv.except_osv(('Warning!!'),('You can have only PHP or Score attached with Device Outright phone purchase type in Postpaid Line.'))
            if jump_soc:
                if jump_soc.is_jump:
                    raise osv.except_osv(('Warning!!'),('You cannot have JUMP attached with Device Outright phone purchase type in Postpaid Line.'))
        return True

    def create(self, cr, uid, vals, context=None):
        res = super(wireless_dsr_postpaid_line, self).create(cr, uid, vals, context=context)
        if vals['dsr_phone_no']:
            phone = vals['dsr_phone_no']
            phone_check(phone)
        if vals['dsr_imei_no'] and vals['dsr_phone_purchase_type']:
            number = vals['dsr_imei_no']
            if vals['dsr_phone_purchase_type'] != 'sim_only':
                imei_check(number)
        if vals['dsr_temp_no']:
            phone = vals['dsr_temp_no']
            temp_check(phone)
        if vals['dsr_sim_no']:
            card_number = vals['dsr_sim_no']
            sim_validation(card_number)
        dsr_phone_purchase_type = vals['dsr_phone_purchase_type']
        jump_soc = vals['jump_soc']
        other_soc = vals['other_soc']
        dsr_jod = vals['dsr_jod']
        self.check_jump_score_php(cr, uid, dsr_phone_purchase_type, jump_soc, other_soc, dsr_jod)
        if vals['data'] or vals['jump'] or vals['intl_feature'] or vals['other']:
            self._create_data_feature(cr, uid, vals, res)
        return res

    def _update_data_feature(self, cr, uid, ids, vals):        
        feature_obj = self.pool.get('wireless.dsr.feature.line')
        prod_obj = self.pool.get('product.product')
        pos_data = self.browse(cr, uid, ids[0])
        imei = pos_data.dsr_imei_no
        phone = pos_data.dsr_phone_no
        sim = pos_data.dsr_sim_no
        product_id = pos_data.product_id.id
        eip_no = pos_data.dsr_eip_no
        ban_no = pos_data.dsr_cust_ban_no
        credit_class = pos_data.dsr_credit_class.id
        dsr_phone_purchase_type = pos_data.dsr_phone_purchase_type
        dsr_temp_no = pos_data.dsr_temp_no
        dsr_trade_inn = pos_data.dsr_trade_inn
        dsr_mob_port = pos_data.dsr_mob_port
        dsr_port_comp = pos_data.dsr_port_comp.id
        dsr_line_no = pos_data.dsr_line_no.id
        dsr_ship_to = pos_data.dsr_ship_to
        is_emp_upg = pos_data.is_emp_upg
        dsr_emp_type = pos_data.dsr_emp_type.id
        dsr_p_number = pos_data.dsr_p_number
        dsr_jod = pos_data.dsr_jod
        if 'jump' in vals:
            if vals['jump'] == False:
                jump_code = pos_data.jump_soc.id
                jump_search_ids = feature_obj.search(cr, uid, [('postpaid_id','=',ids[0]),('dsr_product_code','=',jump_code),('dsr_activiation_interval','=','at_act'),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
                if jump_search_ids:
                    feature_obj.unlink(cr, uid, jump_search_ids)
        if 'data' in vals:
            if vals['data'] == False:
                data_code = pos_data.data_soc.id
                data_search_ids = feature_obj.search(cr, uid, [('postpaid_id','=',ids[0]),('dsr_product_code','=',data_code),('dsr_activiation_interval','=','at_act'),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
                if data_search_ids:
                    feature_obj.unlink(cr, uid, data_search_ids)
        if 'intl_feature' in vals:
            if vals['intl_feature'] == False:
                intl_code = pos_data.intl_feature_soc.id
                intl_search_ids = feature_obj.search(cr, uid, [('postpaid_id','=',ids[0]),('dsr_product_code','=',intl_code),('dsr_activiation_interval','=','at_act'),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
                if intl_search_ids:
                    feature_obj.unlink(cr, uid, intl_search_ids)
        if 'other' in vals:
            if vals['other'] == False:
                other_code = pos_data.other_soc.id
                other_search_ids = feature_obj.search(cr, uid, [('postpaid_id','=',ids[0]),('dsr_product_code','=',other_code),('dsr_activiation_interval','=','at_act'),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
                if other_search_ids:
                    feature_obj.unlink(cr, uid, other_search_ids)
        if 'jump_soc' in vals:
            jump_code = pos_data.jump_soc.id
            jump_search_ids = feature_obj.search(cr, uid, [('postpaid_id','=',ids[0]),('dsr_product_code','=',jump_code),('dsr_activiation_interval','=','at_act'),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
            if jump_search_ids:
                feature_obj.unlink(cr, uid, jump_search_ids)
            prod_jump_browse = prod_obj.browse(cr, uid, vals['jump_soc'])
            if vals['jump_soc']:    
                jump_data = {   'dsr_product_code' : vals['jump_soc'],
                                'feature_product_id':product_id,
                                'dsr_product_type':prod_jump_browse.categ_id.id,
                                'dsr_product_code_type' : prod_jump_browse.dsr_prod_code_type.id,
                                'dsr_monthly_access':prod_jump_browse.monthly_access,
                                'dsr_contract_term':prod_jump_browse.contract_term,
                                'dsr_eip_no':eip_no,
                                'dsr_jump':True,
                                'dsr_phone_no' : phone,
                                'dsr_cust_ban_no' : ban_no,
                                'dsr_sim_no' : sim,
                                'dsr_imei_no' : imei,
                                'dsr_activiation_interval' : 'at_act',
                                'dsr_credit_class' : credit_class,
                                'is_emp_upg':is_emp_upg,
                                'dsr_jod':dsr_jod,
                                'dsr_emp_type':dsr_emp_type,
                                'dsr_p_number':dsr_p_number,
                                'dsr_line_no':dsr_line_no,
                                'postpaid_id' : ids[0],
                                'dsr_temp_no':dsr_temp_no,
                                'dsr_phone_purchase_type':dsr_phone_purchase_type,
                                'dsr_trade_inn':dsr_trade_inn,
                                'dsr_mob_port':dsr_mob_port,
                                'dsr_port_comp':dsr_port_comp,
                                'dsr_ship_to':dsr_ship_to
                            }
                self.pool.get('wireless.dsr.feature.line').create(cr, uid, jump_data)
        if 'data_soc' in vals:
            data_code = pos_data.data_soc.id
            data_search_ids = feature_obj.search(cr, uid, [('postpaid_id','=',ids[0]),('dsr_product_code','=',data_code),('dsr_activiation_interval','=','at_act'),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
            if data_search_ids:
                feature_obj.unlink(cr, uid, data_search_ids)
            prod_data_browse = prod_obj.browse(cr, uid, vals['data_soc'])
            if vals['data_soc']:    
                data = {        'dsr_product_code' : vals['data_soc'],
                                'feature_product_id':product_id,
                                'dsr_product_type':prod_data_browse.categ_id.id,
                                'dsr_product_code_type' : prod_data_browse.dsr_prod_code_type.id,
                                'dsr_monthly_access':prod_data_browse.monthly_access,
                                'dsr_contract_term':prod_data_browse.contract_term,
                                'dsr_eip_no':eip_no,
                                'dsr_jump':True,
                                'dsr_phone_no' : phone,
                                'dsr_cust_ban_no' : ban_no,
                                'dsr_sim_no' : sim,
                                'dsr_imei_no' : imei,
                                'dsr_activiation_interval' : 'at_act',
                                'dsr_credit_class' : credit_class,
                                'is_emp_upg':is_emp_upg,
                                'dsr_jod':dsr_jod,
                                'dsr_emp_type':dsr_emp_type,
                                'dsr_p_number':dsr_p_number,
                                'dsr_line_no':dsr_line_no,
                                'postpaid_id' : ids[0],
                                'dsr_temp_no':dsr_temp_no,
                                'dsr_phone_purchase_type':dsr_phone_purchase_type,
                                'dsr_trade_inn':dsr_trade_inn,
                                'dsr_mob_port':dsr_mob_port,
                                'dsr_port_comp':dsr_port_comp,
                                'dsr_ship_to':dsr_ship_to
                            }
                self.pool.get('wireless.dsr.feature.line').create(cr, uid, data)
        if 'intl_feature_soc' in vals:
            intl_feature_code = pos_data.intl_feature_soc.id
            intl_feature_search_ids = feature_obj.search(cr, uid, [('postpaid_id','=',ids[0]),('dsr_product_code','=',intl_feature_code),('dsr_activiation_interval','=','at_act'),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
            if intl_feature_search_ids:
                feature_obj.unlink(cr, uid, intl_feature_search_ids)
            prod_intl_feature_browse = prod_obj.browse(cr, uid, vals['intl_feature_soc'])
            if vals['intl_feature_soc']:
                intl_feature_data = {   'dsr_product_code' : vals['intl_feature_soc'],
                                'feature_product_id':product_id,
                                'dsr_product_type':prod_intl_feature_browse.categ_id.id,
                                'dsr_product_code_type' : prod_intl_feature_browse.dsr_prod_code_type.id,
                                'dsr_monthly_access':prod_intl_feature_browse.monthly_access,
                                'dsr_contract_term':prod_intl_feature_browse.contract_term,
                                'dsr_eip_no':eip_no,
                                'dsr_jump':True,
                                'dsr_phone_no' : phone,
                                'dsr_cust_ban_no' : ban_no,
                                'dsr_sim_no' : sim,
                                'dsr_imei_no' : imei,
                                'dsr_activiation_interval' : 'at_act',
                                'dsr_credit_class' : credit_class,
                                'is_emp_upg':is_emp_upg,
                                'dsr_jod':dsr_jod,
                                'dsr_emp_type':dsr_emp_type,
                                'dsr_p_number':dsr_p_number,
                                'dsr_line_no':dsr_line_no,
                                'postpaid_id' : ids[0],
                                'dsr_temp_no':dsr_temp_no,
                                'dsr_phone_purchase_type':dsr_phone_purchase_type,
                                'dsr_trade_inn':dsr_trade_inn,
                                'dsr_mob_port':dsr_mob_port,
                                'dsr_port_comp':dsr_port_comp,
                                'dsr_ship_to':dsr_ship_to
                            }
                self.pool.get('wireless.dsr.feature.line').create(cr, uid, intl_feature_data)
        if 'other_soc' in vals:
            other_code = pos_data.other_soc.id
            other_search_ids = feature_obj.search(cr, uid, [('postpaid_id','=',ids[0]),('dsr_product_code','=',other_code),('dsr_activiation_interval','=','at_act'),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
            if other_search_ids:
                feature_obj.unlink(cr, uid, other_search_ids)
            prod_other_browse = prod_obj.browse(cr, uid, vals['other_soc'])
            if vals['other_soc']:
                other_data = {  'dsr_product_code' : vals['other_soc'],
                                'feature_product_id':product_id,
                                'dsr_product_type':prod_other_browse.categ_id.id,
                                'dsr_product_code_type' : prod_other_browse.dsr_prod_code_type.id,
                                'dsr_monthly_access':prod_other_browse.monthly_access,
                                'dsr_contract_term':prod_other_browse.contract_term,
                                'dsr_eip_no':eip_no,
                                'dsr_jump':True,
                                'dsr_phone_no' : phone,
                                'dsr_cust_ban_no' : ban_no,
                                'dsr_sim_no' : sim,
                                'dsr_imei_no' : imei,
                                'dsr_activiation_interval' : 'at_act',
                                'dsr_credit_class' : credit_class,
                                'is_emp_upg':is_emp_upg,
                                'dsr_jod':dsr_jod,
                                'dsr_emp_type':dsr_emp_type,
                                'dsr_p_number':dsr_p_number,
                                'dsr_line_no':dsr_line_no,
                                'postpaid_id' : ids[0],
                                'dsr_temp_no':dsr_temp_no,
                                'dsr_phone_purchase_type':dsr_phone_purchase_type,
                                'dsr_trade_inn':dsr_trade_inn,
                                'dsr_mob_port':dsr_mob_port,
                                'dsr_port_comp':dsr_port_comp,
                                'dsr_ship_to':dsr_ship_to
                            }
                self.pool.get('wireless.dsr.feature.line').create(cr, uid, other_data)
        df_search = feature_obj.search(cr, uid, [('postpaid_id','=',ids[0])])
        if 'dsr_line_no' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_line_no':vals['dsr_line_no']})
        if 'dsr_p_number' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_p_number':vals['dsr_p_number']})
        if 'dsr_credit_class' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_credit_class':vals['dsr_credit_class']})
        if 'dsr_jod' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_jod':vals['dsr_jod']})
        if 'is_emp_upg' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'is_emp_upg':vals['is_emp_upg']})
        if 'dsr_emp_type' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_emp_type':vals['dsr_emp_type']})
        if 'dsr_phone_purchase_type' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_phone_purchase_type':vals['dsr_phone_purchase_type']})
        if 'dsr_phone_no' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_phone_no':vals['dsr_phone_no']})
        if 'dsr_sim_no' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_sim_no':vals['dsr_sim_no']})
        if 'dsr_imei_no' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_imei_no':vals['dsr_imei_no']})
        if 'dsr_temp_no' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_temp_no':vals['dsr_temp_no']})
        if 'dsr_eip_no' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_eip_no':vals['dsr_eip_no']})
        if 'dsr_cust_ban_no' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_cust_ban_no':vals['dsr_cust_ban_no']})
        if 'dsr_trade_inn' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_trade_inn':vals['dsr_trade_inn']})
        if 'dsr_mob_port' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_mob_port':vals['dsr_mob_port']})
        if 'dsr_port_comp' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_port_comp':vals['dsr_port_comp']})
        if 'dsr_ship_to' in vals:
            if df_search:
                for df_search_id in df_search:
                    feature_obj.write(cr, uid, [df_search_id], {'dsr_ship_to':vals['dsr_ship_to']})
        return True

    def write(self, cr, uid, ids, vals, context=None):        
        for id in ids:
            self_obj = self.browse(cr, uid, id)
            if 'dsr_phone_no' in vals:
                phone = vals['dsr_phone_no']
                phone_check(phone)
            
            if vals.has_key('dsr_phone_purchase_type'):
                dsr_phone_purchase_type = vals['dsr_phone_purchase_type']
            else:
                dsr_phone_purchase_type = self_obj.dsr_phone_purchase_type
            
            if 'jump_soc' in vals:
                jump_soc = vals['jump_soc']
            else:
                jump_soc = self_obj.jump_soc.id
            
            if 'other_soc' in vals:
                other_soc = vals['other_soc']
            else:
                other_soc = self_obj.other_soc.id

            if 'dsr_jod' in vals:
                dsr_jod = vals['dsr_jod']
            else:
                dsr_jod = self_obj.dsr_jod

            if 'dsr_imei_no' in vals:
                number = vals['dsr_imei_no']
                if dsr_phone_purchase_type != 'sim_only':
                    imei_check(number)

            if 'dsr_temp_no' in vals:
                phone = vals['dsr_temp_no']
                temp_check(phone)
            
            if 'dsr_sim_no' in vals:
                card_number = vals['dsr_sim_no']
                sim_validation(card_number)
            if 'dsr_rev_gen' in vals:
                vals.update({'dsr_rev_gen_exp':vals['dsr_rev_gen']})
            if 'dsr_comm_amnt' in vals:
                vals.update({'dsr_comm_amnt_exp':vals['dsr_comm_amnt']})
            if 'dsr_comm_spiff' in vals:
                vals.update({'dsr_comm_spiff_exp':vals['dsr_comm_spiff']})
            if 'dsr_comm_added' in vals:
                vals.update({'dsr_comm_added_exp':vals['dsr_comm_added']})
            if 'dsr_tot_rev_gen' in vals:
                vals.update({'dsr_tot_rev_gen_exp':vals['dsr_tot_rev_gen']})
            if 'state' in vals:
                state = vals['state']
            else:
                state = self_obj.state
            if state != 'draft':
               self.check_jump_score_php(cr, uid, dsr_phone_purchase_type, jump_soc, other_soc, dsr_jod)
            self._update_data_feature(cr, uid, [id], vals)
        res = super(wireless_dsr_postpaid_line, self).write(cr, uid, ids, vals, context=context)
        return res

    def unlink(self, cr, uid, ids, context=None):
        feature_obj = self.pool.get('wireless.dsr.feature.line')
        pos_data = self.browse(cr, uid, ids[0])        
        imei = pos_data.dsr_imei_no
        phone = pos_data.dsr_phone_no
        sim = pos_data.dsr_sim_no
        if pos_data.jump == True:
            jump_code = pos_data.jump_soc.id
            jump_search_ids = feature_obj.search(cr, uid, [('postpaid_id','=',ids[0]),('dsr_product_code','=',jump_code),('dsr_activiation_interval','=','at_act'),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
            if jump_search_ids:
                feature_obj.unlink(cr, uid, jump_search_ids)
        if pos_data.data == True:
            data_code = pos_data.data_soc.id
            data_search_ids = feature_obj.search(cr, uid, [('postpaid_id','=',ids[0]),('dsr_product_code','=',data_code),('dsr_activiation_interval','=','at_act'),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
            if data_search_ids:
                feature_obj.unlink(cr, uid, data_search_ids)
        if pos_data.intl_feature == True:
            intl_code = pos_data.intl_feature_soc.id
            intl_search_ids = feature_obj.search(cr, uid, [('postpaid_id','=',ids[0]),('dsr_product_code','=',intl_code),('dsr_activiation_interval','=','at_act'),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
            if intl_search_ids:
                feature_obj.unlink(cr, uid, intl_search_ids)
        if pos_data.other == True:
            other_code = pos_data.other_soc.id
            other_search_ids = feature_obj.search(cr, uid, [('postpaid_id','=',ids[0]),('dsr_product_code','=',other_code),('dsr_activiation_interval','=','at_act'),('dsr_phone_no','=',phone),('dsr_imei_no','=',imei),('dsr_sim_no','=',sim)])
            if other_search_ids:
                feature_obj.unlink(cr, uid, other_search_ids)
        res = super(wireless_dsr_postpaid_line, self).unlink(cr, uid, ids, context=context)
        return res
        
wireless_dsr_postpaid_line()

################# Designation Tracker in HR Employee master ###################
class designation_tracker(osv.osv):
    _name = 'designation.tracker'
    _columns = {
                'designation_id':fields.many2one('hr.job', 'Job', required=True),
                'start_date':fields.date('Start Date', required=True),
                'end_date':fields.date('End Date', required=True),
                'dealer_id':fields.many2one('hr.employee', 'Employee'),
                'store_name': fields.many2one('sap.store', 'Sap Number'),
                'market_id':fields.many2one('market.place', 'Market'),
                'heirarchy_level':fields.char('Heirarchy Level', size=10),
                # 'tracker_str_type':fields.selection(_tracker_str_type, 'Transaction Type'),
                'covering_str_check':fields.boolean('Covering Store'),
                'region_id':fields.many2one('market.regions', 'Region'),
                'covering_market_check':fields.boolean('Covering Market'),
                'covering_region_check':fields.boolean('Covering Region'),
                't_store_id': fields.many2many('sap.store', 'desig_id_sap_id', 'desig_id', 'sap_id', 'Trainee Sap Number',help="Markets assigned to or managed by these employee"),
                't_market_id': fields.many2many('market.place', 'desig_id_market_id', 'desig_id', 'market_id', 'Trainee Market',help="Markets assigned to or managed by these employee"),
                't_region_id': fields.many2many('market.regions', 'desig_id_region_id', 'desig_id', 'region_id', 'Trainee Region',help="Markets assigned to or managed by these employee"),

    }

    def onchange_designation_id(self, cr, uid, ids, designation_id):
        job_obj = self.pool.get('hr.job')
        if designation_id:
            desig_level = job_obj.browse(cr, uid, designation_id).desig_level or False
            return {'value':{'heirarchy_level':desig_level, 'covering_str_check':False, 'covering_market_check':False, 'covering_region_check':False,'store_name':'', 'market_id':'','region_id':''}}
        return {'value':{'heirarchy_level':False}}

    @api.onchange('t_store_id','t_market_id','t_region_id')
    def check_trainee(self):
    	if self.t_store_id:
            self.t_market_id=False
            self.t_region_id=False
    	if self.t_market_id:
            self.t_store_id=False
            self.t_region_id=False
    	if self.t_region_id:
            self.t_store_id=False
            self.t_market_id=False

    def create(self, cr, uid, vals, context=None):
    #####Object creation
        dealer_class = self.pool.get('dealer.class')
        hr_tab = self.pool.get('hr.employee')
        res_users_obj = self.pool.get('res.users')
        hr_job_obj = self.pool.get('hr.job')

        desig_track_obj = self.pool.get('designation.tracker')

        sap_store = self.pool.get('sap.store')
        sap_tracker_obj = self.pool.get('sap.tracker')

        market_tracker_obj = self.pool.get('market.tracker')
        market_place_obj = self.pool.get('market.place')

        region_tracker_obj = self.pool.get('region.tracker')
        market_regions_obj = self.pool.get('market.regions')

    #####Check weather record is updated from sap tracker object or not
        sap_params = False
        if context:
            if 'params' in context:
                context_params = context.get('params')
                if context_params and 'model' in context_params:
                    params_model = context_params.get('model')  
                    if params_model and params_model in ('sap.store','sap.tracker'):
                        sap_params = params_model

    #####res is used in create. hence it's returned on top
        res = super(designation_tracker, self).create(cr, uid, vals, context=context)

    #####Fetch values from vals
        designation_id = vals.get('designation_id',False)
        dealer_id = vals.get('dealer_id',False)
        start_date = vals.get('start_date',False)
        end_date = vals.get('end_date',False)
        heirarchy_level = vals.get('heirarchy_level',False)
        covering_str_check = vals.get('covering_str_check',False)
        store_name = vals.get('store_name',False)
        market_id = vals.get('market_id',False)
        region_id = vals.get('region_id',False)
        covering_market_check = vals.get('covering_market_check',False)
        covering_region_check = vals.get('covering_region_check',False)

    ######## Updating Department based on Job Position ###########
        designation_id = vals.get('designation_id',False)
        if designation_id:
            hr_job_data = hr_job_obj.browse(cr, uid, designation_id)
            department = hr_job_data.department_id.id
            hr_tab.write(cr, uid, dealer_id, {'department_id':department})
            
    #####one date back from start date i.e. yesterday's date
        back_date = (datetime.datetime.strptime(start_date, '%Y-%m-%d')) - timedelta(days=1)        
	
	if designation_id and not heirarchy_level:
	   heirarchy_level = hr_job_obj.browse(cr, uid, designation_id).desig_level or False
    #####Handling
#        if isinstance(end_date, (str)):
#            check_end_date = (datetime.datetime.strptime(end_date, '%Y-%m-%d'))
#        else:
#            check_end_date = end_date
#
#        if isinstance(start_date, (str)):
#            check_start_date = (datetime.datetime.strptime(start_date, '%Y-%m-%d'))
#        else:
#            check_start_date = start_date    

        check_start_date = datetime.datetime.strptime(str(start_date), '%Y-%m-%d')
        check_end_date = datetime.datetime.strptime(str(end_date), '%Y-%m-%d')
    #####Start date is greater than end date
        if (check_start_date and check_end_date) and (check_start_date > check_end_date):
                raise osv.except_osv(('Warning!!!'),('End date should be greater than start date. Check dates you have entered.'))

    #####Start Code Previously written By Krishna
        dealer_search = dealer_class.search(cr, uid, [('start_date','<=',start_date),('end_date','>=',end_date),('dealer_id','=',dealer_id)])
        if dealer_search:
            dealer_class.write(cr, uid, dealer_search, {'designation_id':designation_id})
        hr_tab.write(cr, uid, [dealer_id], {'job_id':designation_id})
    #####End Code Previously written By Krishna


    #####Not allow user to enter designation for same period 
        dealer_data_ids = self.search(cr, uid, [('covering_str_check','=',False),('covering_market_check','=',False),('covering_region_check','=',False),('dealer_id','=',dealer_id),('start_date','<=',start_date),('end_date','>=',end_date)])
        if dealer_data_ids and len(dealer_data_ids) > 1:
            raise osv.except_osv(('Warning!!'),('Period for which you are updating designation already exist.\nCheck the dates you have entered in Designation Tracker.'))

        desig_data_ids = self.search(cr, uid, [('covering_str_check','=',False),('covering_market_check','=',False),('covering_region_check','=',False),('dealer_id','=',dealer_id),('end_date','>=',start_date), ('start_date','<',end_date)])
        if desig_data_ids and len(desig_data_ids) > 1:
            raise osv.except_osv(('Warning!!'),('Previous designation exist on this start date.\nCheck the dates you have entered in Designation Tracker.'))

   #####Start functionality if employee is not RSM, MM and DOS- Create Function
        if heirarchy_level not in ('rsm','mm','dos') :
        #####If dealer id exist
            if dealer_id:
            #####check employee is RSM or not for given period
            #####if yes, it's raise Warning
            #####else it's update his store manager designation in store
                sap_store_ids = desig_track_obj.search(cr, uid, [('dealer_id','=',dealer_id),('end_date','>=',start_date)])
                if sap_store_ids and len(sap_store_ids)>1:
                    raise osv.except_osv(('Warning!!!'),('Employee previous designation is exist for this period.\nCheck designation_tracker records'))
                else:
                #####Check weather existing employee is store manager of store
                #####Store is search by his latest end date in designation tracker when his designation is RSM
                    ext_desig_track_ids = desig_track_obj.search(cr, uid, [('dealer_id','=',dealer_id),('heirarchy_level','=','rsm')], order='end_date desc')
                    if ext_desig_track_ids:
                        for ext_desig_track_id in ext_desig_track_ids:
                            ext_store_id = desig_track_obj.browse(cr,uid,ext_desig_track_id).store_name.id or False
                            if ext_store_id:
                                ext_store_mgr_id = sap_store.browse(cr, uid, [ext_store_id]).store_mgr_id.id or False
                                if dealer_id == ext_store_mgr_id:
                                    sap_store.write(cr,uid,[ext_store_id],{'store_mgr_id':False})
                #####Check weather existing employee is Market manager of Market
                #####Market is search by his latest end date in designation tracker when his designation not MM
                    ext_desig_track_ids = desig_track_obj.search(cr, uid, [('dealer_id','=',dealer_id),('heirarchy_level','=','mm')], order='end_date desc')
                    
                    if ext_desig_track_ids:
                        for ext_desig_track_id in ext_desig_track_ids:
                            ext_market_id = desig_track_obj.browse(cr,uid,ext_desig_track_ids[0]).market_id.id or False
                            if ext_market_id:
                                ext_market_mgr_id = market_place_obj.browse(cr, uid, [ext_market_id]).market_manager.id or False
                                if dealer_id == ext_market_mgr_id:
                                    market_tracker_id = market_tracker_obj.search(cr,uid,[('desig_id','=',res)])
                                    if market_tracker_id:
                                       market_tracker_obj.unlink(cr,uid,market_tracker_id[0])
                                    market_place_obj.write(cr,uid,[ext_market_id],{'market_manager':False})    
                    
                #####Check weather existing employee is Sales Director of Region
                #####Region is search by his latest end date in designation tracker when his designation not DOS
                    ext_desig_track_ids = desig_track_obj.search(cr, uid, [('dealer_id','=',dealer_id),('heirarchy_level','=','dos')], order='end_date desc')
                    
                    if ext_desig_track_ids:
                        for ext_desig_track_id in ext_desig_track_ids:
                            ext_region_id = desig_track_obj.browse(cr,uid,ext_desig_track_ids[0]).region_id.id or False
                            if ext_region_id:
                                ext_dos_id = market_regions_obj.browse(cr, uid, [ext_region_id]).sales_director.id or False
                                if dealer_id == ext_dos_id:
                                    region_tracker_id = region_tracker_obj.search(cr,uid,[('desig_id','=',res)])
                                    if region_tracker_id:
                                        region_tracker_obj.unlink(cr,uid,region_tracker_id[0])
                                    market_regions_obj.write(cr,uid,[ext_region_id],{'sales_director':False})                                                              
    #####End functionality for RSA and all

    #####Start functionality for RSM
        if heirarchy_level == 'rsm' and vals.has_key('store_name') and vals['store_name'] and \
            vals.has_key('covering_str_check'):

            if store_name and res:

                sap_store_obj = sap_store.browse(cr,uid,store_name)
                store_sap_number = sap_store_obj.sap_number or False
                if store_sap_number:
                    store_sap_number = str(store_sap_number)
                store_sap_name = sap_store_obj.name or False
        ######Start Handlings Create Function - RSM
                cr.execute('select id from sap_tracker where sap_id = %s and (desig_id != %s or store_mgr_id is null) order by end_date desc'%(str(store_name),str(res)))
                sap_track_ids = map(lambda x: x[0], cr.fetchall())
                #sap_track_ids = sap_tracker_obj.search(cr, uid, [('sap_id','=',store_name),('desig_id','!=',res)],order='end_date desc')
                if sap_track_ids:
                    end_date_list = sap_tracker_obj.browse(cr,uid,sap_track_ids[0]).end_date or False
                    if isinstance(end_date_list, (str)):
                        end_date_list = (datetime.datetime.strptime(end_date_list, '%Y-%m-%d'))
                    else:
                        end_date_list = end_date_list

                    if (check_start_date and end_date_list) and (check_start_date <= end_date_list):
                        if store_sap_name and store_sap_number:
                            raise osv.except_osv(('Warning!!!'),('Store Manager exists at Store:'+store_sap_name+','+store_sap_number+'\nPlease assign to a store where Store Manager does not exist.'))
                        else:
                            raise osv.except_osv(('Warning!!!'),('Store Manager exists at Store.\nPlease assign to a store where Store Manager does not exist.'))

                    for sap_track_id in sap_track_ids:
                        start_date_list = sap_tracker_obj.browse(cr,uid,sap_track_id).start_date or False
                        if isinstance(start_date_list, (str)):
                            start_date_list = (datetime.datetime.strptime(start_date_list, '%Y-%m-%d'))
                        else:
                            start_date_list = start_date_list
                        if (start_date_list and check_start_date) and (check_start_date <= start_date_list):
                            raise osv.except_osv(('Warning!!!'),('Start date shoud be greater. Check start date in store ',store_sap_number))       
                        if (check_end_date and start_date_list) and (check_end_date <= start_date_list):
                           raise osv.except_osv(('Warning!!!'),('End date shoud be greater. Check start date in store ',store_sap_number))       

            if covering_str_check == False:
                covering_str_check_ids = self.search(cr, uid, [('dealer_id','=',dealer_id),('store_name','!=',False),('covering_str_check','=',False),('end_date','>=',start_date)])
                if covering_str_check_ids and len(covering_str_check_ids) > 1:
                    raise osv.except_osv(('Warning!!!'),('You can not have two base stores assigned within same period.\nPlease check stores you have entered in designation tracker.'))
        ######End Handlings Create Function - RSM

            #update manager in sap store
            if store_name and dealer_id:
                sap_store.write(cr, uid, store_name,{'store_mgr_id':dealer_id})

            ext_market_id = sap_store.browse(cr,uid,store_name).market_id.id or False
            if not sap_params and start_date and end_date:
                sap_tracker_obj.create(cr, uid, {'sap_id':store_name, 'store_mgr_id':dealer_id,'market_id':ext_market_id,'start_date':start_date,'end_date':end_date,'desig_id':res,'store_inactive':False,'store_comments':False,'designation_id':designation_id})
            #####Start Update designation -RSM

        #####Check weather existing employee is Market manager of Market
        #####Market is search by his latest end date in designation tracker when his designation not MM
            ext_desig_track_ids = desig_track_obj.search(cr, uid, [('dealer_id','=',dealer_id),('heirarchy_level','=','mm'),('end_date','<=',check_start_date)], order='end_date desc')
            
            if ext_desig_track_ids:
                for ext_desig_track_id in ext_desig_track_ids:
                    ext_market_id = desig_track_obj.browse(cr,uid,ext_desig_track_id).market_id.id or False
                    if ext_market_id:
                        ext_market_mgr_id = market_place_obj.browse(cr, uid, [ext_market_id]).market_manager.id or False
                        if dealer_id == ext_market_mgr_id:                            
                            market_place_obj.write(cr,uid,[ext_market_id],{'market_manager':False})
                            market_tracker_id = market_tracker_obj.search(cr,uid,[('desig_id','=',res)])
                            if market_tracker_id:
                                market_tracker_obj.unlink(cr,uid,market_tracker_id[0])    

            ext_desig_track_ids = desig_track_obj.search(cr, uid, [('covering_market_check','=',True),('dealer_id','=',dealer_id),('heirarchy_level','=','mm'),('end_date','<=',check_start_date)], order='end_date desc')
            
            if ext_desig_track_ids:
                for ext_desig_track_id in ext_desig_track_ids:
                    ext_market_id = desig_track_obj.browse(cr,uid,ext_desig_track_id).market_id.id or False
                    if ext_market_id:
                        ext_market_mgr_id = market_place_obj.browse(cr, uid, [ext_market_id]).market_manager.id or False
                        if dealer_id == ext_market_mgr_id:                            
                            market_place_obj.write(cr,uid,[ext_market_id],{'market_manager':False})
                            market_tracker_id = market_tracker_obj.search(cr,uid,[('desig_id','=',res)])
                            if market_tracker_id:
                                market_tracker_obj.unlink(cr,uid,market_tracker_id[0])                                 
        #####Check weather existing employee is Sales Director of Region
        #####Region is search by his latest end date in designation tracker when his designation not DOS
            
            ext_desig_track_ids = desig_track_obj.search(cr, uid, [('dealer_id','=',dealer_id),('heirarchy_level','=','dos'),('end_date','<=',start_date)], order='end_date desc')
            
            if ext_desig_track_ids:
                for ext_desig_track_id in ext_desig_track_ids:
                    ext_region_id = desig_track_obj.browse(cr,uid,ext_desig_track_id).region_id.id
                    if ext_region_id:
                        ext_dos_id = market_regions_obj.browse(cr, uid, [ext_region_id]).sales_director.id
                        if dealer_id == ext_dos_id:
                            market_regions_obj.write(cr,uid,[ext_region_id],{'sales_director':False})
                            region_tracker_id = region_tracker_obj.search(cr,uid,[('desig_id','=',res)])
                            if region_tracker_id:
                                region_tracker_obj.unlink(cr,uid,region_tracker_id[0])    
                            
            ext_desig_track_ids = desig_track_obj.search(cr, uid, [('covering_region_check','=',True),('dealer_id','=',dealer_id),('heirarchy_level','=','dos'),('end_date','<=',start_date)], order='end_date desc')
            
            if ext_desig_track_ids:
                for ext_desig_track_id in ext_desig_track_ids:
                    ext_region_id = desig_track_obj.browse(cr,uid,ext_desig_track_id).region_id.id
                    if ext_region_id:
                        ext_dos_id = market_regions_obj.browse(cr, uid, [ext_region_id]).sales_director.id
                        if dealer_id == ext_dos_id:
                            market_regions_obj.write(cr,uid,[ext_region_id],{'sales_director':False})                                                      
    #####End Update designation - RSM   
    #####End functionality for RSM - Create Function

    #####Start functionality for MM -Create Function
        if heirarchy_level == 'mm' and vals.has_key('market_id') and vals['market_id']:
	    logger.info("------------------Start functionality for MM -Create Function")
            market_tracker_ids = ''
            market_id_obj = market_place_obj.browse(cr,uid,market_id) or False
            if market_id_obj:
                market_name = market_id_obj.name
                target_market_region = market_id_obj.region_market_id.id
                target_market_manager = market_id_obj.market_manager.id
            else:
                market_name = ''
                target_market_region = ''
                target_market_manager = ''         

            if market_id and res:
                cr.execute('select id from market_tracker where market_id = %s and (desig_id != %s or market_manager is null) order by end_date desc'%(str(market_id),str(res)))
                market_tracker_ids = map(lambda x: x[0], cr.fetchall())
		
                if market_tracker_ids:
                    end_date_list = market_tracker_obj.browse(cr,uid,market_tracker_ids[0]).end_date or False
                    if isinstance(end_date_list, (str)):
                        end_date_list = (datetime.datetime.strptime(end_date_list, '%Y-%m-%d'))
			logger.info("--------------------if =============end_date_list")
                    else:
                        end_date_list = end_date_list
			logger.info("-----------------else end_date_list")
		    logger.info("-------if (check_start_date and end_date_list) and (check_start_date <= end_date_list)%s %s %s %s"%(check_start_date,end_date_list,type(check_start_date),type(end_date_list)))
                    if check_start_date and end_date_list and (check_start_date <= end_date_list):
			logger.info("-------if (check_start_date and end_date_list-------------")
                        if market_name:
                            raise osv.except_osv(('Warning!!!'),('Market Manager/Market Tracker Record exists at market:: '+market_name+'\nPlease assign to a store where Market Manager does not exist.'))
                        else:
                            raise osv.except_osv(('Warning!!!'),('Market Manager/Market Tracker Record exists at market.\nPlease assign to a store where Market Manager does not exist.'))

#                    for market_tracker_id in market_tracker_ids:
#                        start_date_list = market_tracker_obj.browse(cr,uid,market_tracker_id).start_date
#                        if isinstance(start_date_list, (str)):
#                            start_date_list = (datetime.datetime.strptime(start_date_list, '%Y-%m-%d'))
#                        else:
#                            start_date_list = start_date_list
#
#                        if (check_start_date and start_date_list) and (check_start_date <= start_date_list):
#                            raise osv.except_osv(('Warning!!!'),('Start date shoud be greater. Check start date in market - '+market_name))       
#                        if (check_end_date and start_date_list) and (check_end_date <= start_date_list):
#                            raise osv.except_osv(('Warning!!!'),('End date shoud be greater. Check start date in market - '+market_name))  
       #####Update Market data
       #####Start Update Designation - MM
	    logger.info("----------Start Update Designation - MM")
            if dealer_id and market_id:
                market_place_obj.write(cr,uid,[market_id],{'market_manager':dealer_id})
            if start_date and end_date:
                market_tracker_obj.create(cr,uid,{'region_market_id':target_market_region, 'market_manager':dealer_id, 'market_id':market_id, 'end_date': end_date, 'start_date': start_date, 'desig_id':res,'designation_id':designation_id})
             
        #####Check weather existing employee is Store Manager of Store
        #####Store is search by his latest end date in designation tracker when his designation not RSM
            ext_desig_track_ids = desig_track_obj.search(cr, uid, [('dealer_id','=',dealer_id),('heirarchy_level','=','rsm'),('end_date','<=',start_date)], order='end_date desc')
            if ext_desig_track_ids:
                for ext_desig_track_id in ext_desig_track_ids:
                    ext_store_id = desig_track_obj.browse(cr,uid,ext_desig_track_id).store_name.id or False
                    if ext_store_id:
                        sap_store = self.pool.get('sap.store')          
                        ext_store_mgr_id = sap_store.browse(cr, uid, [ext_store_id]).store_mgr_id.id or False
                        if dealer_id == ext_store_mgr_id:
                            sap_store.write(cr,uid,[ext_store_id],{'store_mgr_id':False})
        ####For covering check store
            ext_desig_track_ids = desig_track_obj.search(cr, uid, [('covering_str_check','=',True),('dealer_id','=',dealer_id),('heirarchy_level','=','rsm'),('end_date','<=',start_date)],order='end_date desc')
            if ext_desig_track_ids:
                for ext_desig_track_id in ext_desig_track_ids:
                    ext_store_id = desig_track_obj.browse(cr,uid,ext_desig_track_id).store_name.id
                    if ext_store_id:
                        sap_store = self.pool.get('sap.store')
                        ext_store_mgr_id = sap_store.browse(cr, uid, [ext_store_id]).store_mgr_id.id
                        if dealer_id == ext_store_mgr_id:
                            sap_store.write(cr,uid,[ext_store_id],{'store_mgr_id':False})
        #####Check weather existing employee is Sales Director of Region
        #####Region is search by his latest end date in designation tracker when his designation not DOS            
            ext_desig_track_ids = desig_track_obj.search(cr, uid, [('dealer_id','=',dealer_id),('heirarchy_level','=','dos'),('end_date','<=',start_date)], order='end_date desc')
            
            if ext_desig_track_ids:
                for ext_desig_track_id in ext_desig_track_ids:
                    ext_region_id = desig_track_obj.browse(cr,uid,ext_desig_track_id).region_id.id
                    if ext_region_id:
                        ext_dos_id = market_regions_obj.browse(cr, uid, [ext_region_id]).sales_director.id
                        if dealer_id == ext_dos_id:
                            market_regions_obj.write(cr,uid,[ext_region_id],{'sales_director':False})

            ext_desig_track_ids = desig_track_obj.search(cr, uid, [('covering_region_check','=',True),('dealer_id','=',dealer_id),('heirarchy_level','=','dos'),('end_date','<=',start_date)], order='end_date desc')
            
            if ext_desig_track_ids:
                for ext_desig_track_id in ext_desig_track_ids:
                    ext_region_id = desig_track_obj.browse(cr,uid,ext_desig_track_id).region_id.id
                    if ext_region_id:
                        ext_dos_id = market_regions_obj.browse(cr, uid, [ext_region_id]).sales_director.id
                        if dealer_id == ext_dos_id:
                            market_regions_obj.write(cr,uid,[ext_region_id],{'sales_director':False})                                             
        #####End Update Designation - MM                               
	    logger.info("----------------End Update Designation - MM")
    #####End functionality for MM - Create Function

    #####Start functionality for DOS - Create Function
        if heirarchy_level == 'dos' and vals.has_key('region_id') and vals['region_id']:
            region_tracker_ids = ''
            region_id_obj = market_regions_obj.browse(cr,uid,region_id) or False
            if region_id_obj:
                region_name = region_id_obj.name
            else:
                region_name = ''
            if region_id and res:
                cr.execute('select id from region_tracker where region_id = %s and (desig_id != %s or sales_director is null) order by end_date desc'%(str(region_id),str(res)))
                region_tracker_ids = map(lambda x: x[0], cr.fetchall())

                if region_tracker_ids:
                    end_date_list = region_tracker_obj.browse(cr,uid,region_tracker_ids[0]).end_date or False
                    if isinstance(end_date_list, (str)):
                        end_date_list = (datetime.datetime.strptime(end_date_list, '%Y-%m-%d'))
                    else:
                        end_date_list = end_date_list                    
                    if (check_start_date and end_date_list) and (check_start_date <= end_date_list):
			logger.info("context------%s---check_start_date ---%s----end_date_list----%s----region_tracker_ids----%s---res%s"%(context,check_start_date,end_date_list,region_tracker_ids,res))
                        if region_name:
                            raise osv.except_osv(('Warning!!!'),('Director of Sales/Region Tracker record exists at region: '+region_name+'\nPlease assign to a region where Director of Sales does not exist.'))
                        else:
                            raise osv.except_osv(('Warning!!!'),('Director of Sales exists/Region Tracker record at region.\nPlease assign to a region where Director of Sales does not exist.'))
#                    for region_tracker_id in region_tracker_ids:
#                        start_date_list = region_tracker_obj.browse(cr,uid,region_tracker_id).start_date
#                        if start_date_list and isinstance(start_date_list, (str)):
#                            start_date_list = (datetime.datetime.strptime(start_date_list, '%Y-%m-%d'))
#                        else:
#                            start_date_list = start_date_list
#                        if (check_start_date and start_date_list) and (check_start_date <= start_date_list):
#                            raise osv.except_osv(('Warning!!!'),('Start date shoud be greater. Check start date in region - '+region_name))       
#                        if (check_end_date and start_date_list) and (check_end_date <= start_date_list):
#                           raise osv.except_osv(('Warning!!!'),('End date shoud be greater. Check start date in region - '+region_name))  

        #####Fetch Target Region data
            emp_no = hr_tab.browse(cr,uid,dealer_id).emp_no or False
            target_company_id = False
        ##### Fetch company id
        ##### hr_employee(emp_no)-res_users(login)-res_users(company_id)
            if emp_no:
                res_users_id = res_users_obj.search(cr,uid,[('login','=',emp_no)])
                if res_users_id:
                    target_company_id = res_users_obj.browse(cr,uid,res_users_id[0]).company_id.id or False
    #####Start Update Designation - DOS 
        #####Update DOS in Region
            if dealer_id and region_id:
                market_regions_obj.write(cr,uid,[region_id],{'sales_director':dealer_id})
        #####Create new region tracker in Region
            if start_date and end_date:
                region_tracker_ids = region_tracker_obj.search(cr,uid,[('desig_id','=',res),('region_id','=',region_id)])
                if not region_tracker_ids:
	            region_tracker_obj.create(cr,uid,{'company_id':target_company_id, 'sales_director':dealer_id, 'region_id':region_id, 'end_date': end_date, 'start_date': start_date, 'desig_id':res,'designation_id':designation_id})
                    
        #####Check weather existing employee is Store Manager of Store
        #####Store is search by his latest end date in designation tracker when his designation not RSM

            ext_desig_track_ids = desig_track_obj.search(cr, uid, [('dealer_id','=',dealer_id),('heirarchy_level','=','rsm'),('end_date','<=',start_date)], order='end_date desc')

            if ext_desig_track_ids:
                ext_store_id = desig_track_obj.browse(cr,uid,ext_desig_track_ids[0]).store_name.id
                if ext_store_id:
                    sap_store = self.pool.get('sap.store')
                    ext_store_mgr_id = sap_store.browse(cr, uid, [ext_store_id]).store_mgr_id.id
                    if dealer_id == ext_store_mgr_id:
                        sap_store.write(cr,uid,[ext_store_id],{'store_mgr_id':False})


        ####For covering check store
            ext_desig_track_ids = desig_track_obj.search(cr, uid, [('covering_str_check','=',True),('dealer_id','=',dealer_id),('heirarchy_level','=','rsm'),('end_date','<=',start_date)], order='end_date desc')
            if ext_desig_track_ids:
                ext_store_id = desig_track_obj.browse(cr,uid,ext_desig_track_ids[0]).store_name.id
                if ext_store_id:
                    sap_store = self.pool.get('sap.store')
                    ext_store_mgr_id = sap_store.browse(cr, uid, [ext_store_id]).store_mgr_id.id
                    if dealer_id == ext_store_mgr_id:
                        sap_store.write(cr,uid,[ext_store_id],{'store_mgr_id':False})

        #####Check weather existing employee is Market manager of Market
        #####Market is search by his latest end date in designation tracker when his designation not MM
            
            ext_desig_track_ids = desig_track_obj.search(cr, uid, [('dealer_id','=',dealer_id),('heirarchy_level','=','mm'),('end_date','<=',start_date)], order='end_date desc')
            
            if ext_desig_track_ids:
                ext_market_id = desig_track_obj.browse(cr,uid,ext_desig_track_ids[0]).market_id.id
                if ext_market_id:
                    ext_market_mgr_id = market_place_obj.browse(cr, uid, [ext_market_id]).market_manager.id
                    if dealer_id == ext_market_mgr_id:
                        market_place_obj.write(cr,uid,[ext_market_id],{'market_manager':False}) 

            ext_desig_track_ids = desig_track_obj.search(cr, uid, [('covering_market_check','=',True),('dealer_id','=',dealer_id),('heirarchy_level','=','mm'),('end_date','<=',start_date)], order='end_date desc')            
            if ext_desig_track_ids:
                ext_market_id = desig_track_obj.browse(cr,uid,ext_desig_track_ids[0]).market_id.id
                if ext_market_id:
                    ext_market_mgr_id = market_place_obj.browse(cr, uid, [ext_market_id]).market_manager.id
                    if dealer_id == ext_market_mgr_id:
                        market_place_obj.write(cr,uid,[ext_market_id],{'market_manager':False})                         
                                
        #####End Update Designation - DOS            
        #####End Functionality of DOS - Create Function  

    #####Start Covering Store Newly developed Functionality - Create Function
        if dealer_id and not covering_str_check:
            sap_store_ids = sap_store.search(cr,uid,[('store_mgr_id','=',dealer_id)])
            cr.execute('select store_id from hr_id_store_id where hr_id = %s'%(dealer_id))
            hr_id_store_id = map(lambda x: x[0], cr.fetchall())

            if hr_id_store_id and sap_store_ids:
                delete_records = list(set(hr_id_store_id) - set(sap_store_ids))
                insert_records = list(set(sap_store_ids) - set(hr_id_store_id))

                if delete_records:
                    for delete_record in delete_records:
                        cr.execute('delete from hr_id_store_id where hr_id = %s and store_id = %s',(dealer_id,delete_record))
                if insert_records:
                    for insert_record in insert_records:
                        cr.execute('select * from hr_id_store_id where hr_id = %s and store_id = %s',(dealer_id,insert_record))
                        ext_hr_id_store_id = map(lambda x: x[0], cr.fetchall())
                        if not ext_hr_id_store_id:
                            cr.execute('insert into hr_id_store_id (hr_id, store_id) values(%s,%s)',(dealer_id,insert_record))
        #####If there have sap_store_ids only but there is no data will presnt in covering store
        #####It'll insert new data into covering store
            elif sap_store_ids:
                for sap_store_id in sap_store_ids:
                    cr.execute('select * from hr_id_store_id where hr_id = %s and region_id = %s',(dealer_id,sap_store_id))
                    ext_hr_id_store_id = map(lambda x: x[0], cr.fetchall())
                    if not ext_hr_id_store_id:
                        cr.execute('insert into hr_id_store_id (hr_id, region_id) values(%s,%s)',(dealer_id,sap_store_id))            
        #####If there are records in covering store
        #####but currently that employee is not a RSM of any store
        #####Delete such records from covering store
            else:
                cr.execute('delete from hr_id_store_id where hr_id = %s',(dealer_id,))    
    #####End Covering Store Newly developed Functionality - Create Function


    #####Start Covering Market Functionality - create Function
        #####Get market id in which current employee is assigned as manager    
            market_ids = market_place_obj.search(cr,uid,[('market_manager','=',dealer_id)])
        #####Get the data of covering market table
            cr.execute('select market_id from hr_id_market_id where hr_id = %s'%(dealer_id))
            hr_id_market_id = map(lambda x: x[0], cr.fetchall())
        #####If there have a market id and covering market data
        #####It'll check covering market data with market ids and delete unwanted one 
        #####as well as insert new one   
            if hr_id_market_id and market_ids:
                delete_records = list(set(hr_id_market_id) - set(market_ids))
                insert_records = list(set(market_ids) - set(hr_id_market_id))
            #####if there have any missed match data
            #####It will delete it from covering market
            #####and insert new one in covering market
                if delete_records:
                    for delete_record in delete_records:
                        cr.execute('delete from hr_id_market_id where hr_id = %s and market_id = %s',(dealer_id,delete_record))
                if insert_records:
                    for insert_record in insert_records:
                        cr.execute('select * from hr_id_market_id where hr_id = %s and market_id = %s',(dealer_id,insert_record))
                        ext_hr_id_market_id = map(lambda x: x[0], cr.fetchall())
                        if not ext_hr_id_market_id:
                            cr.execute('insert into hr_id_market_id (hr_id, market_id) values(%s,%s)',(dealer_id,insert_record))
        #####If there have market_ids only but there is no data will presnt in covering market
        #####It'll insert new data into covering market
            elif market_ids:
                for market_id in market_ids:
                    cr.execute('select * from hr_id_market_id where hr_id = %s and market_id = %s',(dealer_id,market_id))
                    ext_hr_id_market_id = map(lambda x: x[0], cr.fetchall())
                    if not ext_hr_id_market_id:
                        cr.execute('insert into hr_id_market_id (hr_id, market_id) values(%s,%s)',(dealer_id,market_id))            
        #####If there are records in covering market
        #####but currently that employee is not a MM of any market
        #####Delete such records from covering market
            else:
                cr.execute('delete from hr_id_market_id where hr_id = %s',(dealer_id,))
    #####End Covering Market Functionality - create Function
    
    #####Start Covering Region Functionality - create Function
        #####Get region id in which current employee is assigned as manager
            region_ids = market_regions_obj.search(cr,uid,[('sales_director','=',dealer_id)])
        #####Get the data of covering region table
            cr.execute('select region_id from hr_id_region_id where hr_id = %s'%(dealer_id))
            hr_id_region_id = map(lambda x: x[0], cr.fetchall())
        #####If there have a region id and covering market data
        #####It'll check covering region data with region ids and delete unwanted one
        #####as well as insert new one   
            if hr_id_region_id and region_ids:
                delete_records = list(set(hr_id_region_id) - set(region_ids))
                insert_records = list(set(region_ids) - set(hr_id_region_id))
            #####if there have any missed match data
            #####It will delete it from covering region
            #####and insert new one in covering region
                if delete_records:
                    for delete_record in delete_records:
                        cr.execute('delete from hr_id_region_id where hr_id = %s and region_id = %s',(dealer_id,delete_record))
                if insert_records:
                    for insert_record in insert_records:
                        cr.execute('select * from hr_id_region_id where hr_id = %s and region_id = %s',(dealer_id,insert_record))
                        ext_hr_id_region_id = map(lambda x: x[0], cr.fetchall())
                        if not ext_hr_id_region_id:
                            cr.execute('insert into hr_id_region_id (hr_id, region_id) values(%s,%s)',(dealer_id,insert_record))
        #####If there have region_id only but there is no data will presnt in covering region
        #####It'll insert new data into covering region
            elif region_ids:
                for region_id in region_ids:
                    cr.execute('select * from hr_id_region_id where hr_id = %s and region_id = %s',(dealer_id,region_id))
                    ext_hr_id_region_id = map(lambda x: x[0], cr.fetchall())
                    if not ext_hr_id_region_id:
                        cr.execute('insert into hr_id_region_id (hr_id, region_id) values(%s,%s)',(dealer_id,region_id))            
        #####If there are records in covering region
        #####but currently that employee is not a DOS of any region
        #####Delete such records from covering region
            else:
                cr.execute('delete from hr_id_region_id where hr_id = %s',(dealer_id,))
    #####End Covering Region Functionality - create Function 


    #####If dealer_id is MM or DOS then make it's Home base store as corporate
        market_mgr_ids = market_place_obj.search(cr,uid,[('market_manager','=',dealer_id)]) or False
        region_mgr_ids = market_regions_obj.search(cr,uid,[('sales_director','=',dealer_id)]) or False
        
        if market_mgr_ids and len(market_mgr_ids)>0:
            sap_store_id = sap_store.search(cr,uid,[('sap_number','=','1')]) or False
            if sap_store_id:
                hr_tab.write(cr,uid,dealer_id,{'store_id':sap_store_id[0]})

        if region_mgr_ids and len(region_mgr_ids)>0:
            sap_store_id = sap_store.search(cr,uid,[('sap_number','=','1')]) or False
            if sap_store_id:                
                hr_tab.write(cr,uid,dealer_id,{'store_id':sap_store_id[0]})
    #####End If dealer_id is MM or DOS then make it's Home base store as corporate
        if dealer_id:
            ext_desig_ids = self.search(cr, uid, [('dealer_id','=',dealer_id)], order='end_date desc')
            if ext_desig_ids:
                ext_designation_id = self.browse(cr,uid,ext_desig_ids[0]).designation_id.id or False
                heirarchy_level_value = self.browse(cr,uid,ext_desig_ids[0]).heirarchy_level or False
                if heirarchy_level_value and heirarchy_level_value == 'rsm':
                    store_name_value = self.browse(cr,uid,ext_desig_ids[0]).store_name.id or False
                else:
                    store_name_value = ''
                if ext_designation_id and store_name_value:
                    hr_tab.write(cr, uid, dealer_id, {'store_id':store_name_value, 'job_id':ext_designation_id})
                elif ext_designation_id:
                    hr_tab.write(cr, uid, dealer_id, {'job_id':ext_designation_id})
    #####Start Assign Access rights - Create Function
    #####Dont't forget to create object of class res_users,hr_job,
        if dealer_id and end_date:
            dealer_id_obj = hr_tab.browse(cr,uid,dealer_id)
            emp_no = dealer_id_obj.emp_no or False
            emp_active = dealer_id_obj.active or False
            res_users_ids = res_users_obj.search(cr,uid,[('login','=',emp_no)])
            if not res_users_ids:
                cr.execute('select id from res_users where login = %s',(emp_no,))
                res_users_ids = map(lambda x: x[0], cr.fetchall()) 

            current_date = datetime.datetime.now(pytz.timezone('US/Mountain'))

        #####search designation tracker id for current employee where start date is greater than current date
            cr_desig_track_ids = desig_track_obj.search(cr, uid, [('dealer_id','=',dealer_id),('end_date','>=',start_date)], order='end_date desc')
            if cr_desig_track_ids and len(cr_desig_track_ids) <= 1:
                
            #####Get designation of the current employee
                cr_designation_id = self.browse(cr,uid,cr_desig_track_ids[0]).designation_id.id or False
                if cr_designation_id:
                #####Check weather that designation have assigned access groups
                    cr.execute('select gid from job_res_group_rel where jid = %s'%(cr_designation_id))
                    cr_access_groups_ids = map(lambda x: x[0], cr.fetchall())
                    if cr_access_groups_ids:
                        if res_users_ids:
                        #####Get access groups ids of that designation i.e. employee current designation
                            cr.execute('select gid from res_groups_users_rel where uid = %s'%(res_users_ids[0]))
                            res_groups_users_rel_ids = map(lambda x: x[0], cr.fetchall())
                        #####If employee have assigned access groups
                        #####then it's delete that access groups first and assign current designation's access groups                            
                            if len(res_groups_users_rel_ids)>0:  
                                if emp_active == True:
                                    cr.execute('delete from res_groups_users_rel where uid = %s'%(res_users_ids[0]))
                                    for cr_access_groups_id in cr_access_groups_ids:
                                        cr.execute('insert into res_groups_users_rel (uid, gid) values(%s,%s)'%(res_users_ids[0],cr_access_groups_id))
                                        logger.info("For external employee id %s access group %s assigned"%(dealer_id, cr_access_groups_id))
                            else:
                                if emp_active == True:
                                    for cr_access_groups_id in cr_access_groups_ids:
                                        cr.execute('insert into res_groups_users_rel (uid, gid) values(%s,%s)'%(res_users_ids[0],cr_access_groups_id))
                                        logger.info("For external employee id %s access group %s assigned"%(dealer_id, cr_access_groups_id))
                        else:
                            raise osv.except_osv(('Warning!!!'),('Employee is not active in res_users'))   
                #####If employee does not have access groups
                #####assign current designation's access groups                            
                    else:
                        raise osv.except_osv(('Warning!!!'),('For this job designation Access group is not assigned. Kindly assign access group first in Job Position and then try.'))   

    #####update latest designation in job title

        
        emp_no = hr_tab.browse(cr,uid,dealer_id).emp_no or False
        values = {}
        if emp_no:
            res_users_id = res_users_obj.search(cr,uid,[('login','=',emp_no)])
            if res_users_id:
                values.update({'login':emp_no})
                res_users_obj.write(cr,uid,res_users_id,values)
        return res


    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}

        if isinstance(ids, (int, long)):
            ids = [ids]
    #####Start Code By Krishna
        dealer_class = self.pool.get('dealer.class')
        hr_tab = self.pool.get('hr.employee')
        self_data = self.browse(cr, uid, ids[0])
        # start_date = self_data.start_date
        # dealer_id = self_data.dealer_id.id
        # designation_id = self_data.designation_id.id
    #####End Code by krishna
        
    #####Start Code by Pratik

    #####Object creation of masters
        desig_track_obj = self.pool.get('designation.tracker')

        sap_store = self.pool.get('sap.store')
        sap_tracker_obj = self.pool.get('sap.tracker')
        
        market_tracker_obj = self.pool.get('market.tracker')
        market_place_obj = self.pool.get('market.place')

        market_tracker_obj = self.pool.get('market.tracker')
        market_place_obj = self.pool.get('market.place')

        region_tracker_obj = self.pool.get('region.tracker')
        market_regions_obj = self.pool.get('market.regions')
        res_users_obj = self.pool.get('res.users')
        hr_job_obj = self.pool.get('hr.job')

    ######## Updating Department based on Job Position ###########
        designation_id = vals.get('designation_id',False)
        if designation_id:
            hr_job_data = hr_job_obj.browse(cr, uid, designation_id)
            department = hr_job_data.department_id.id
            hr_tab.write(cr, uid, self_data.dealer_id.id, {'department_id':department})

    #####Get all values from values
    #####if not exist in vals it'll get it from line directly
        if 'start_date' in vals:
            start_date = vals['start_date']
        else:
            start_date = self_data.start_date or False
        
        if 'end_date' in vals:
            end_date = vals['end_date']
        else:
            end_date = self_data.end_date or False
                    
        if 'covering_str_check' in vals:
            covering_str_check = vals['covering_str_check']
        else:
            covering_str_check = self_data.covering_str_check or False
        
        if 'store_name' in vals:
            store_name = vals['store_name']
        else:
            store_name = self_data.store_name.id or False
        
        if 'dealer_id' in vals:
            dealer_id = vals['dealer_id']
        else:
            dealer_id = self_data.dealer_id.id or False

        if 'designation_id' in vals:
            designation_id = vals['designation_id']
        else:
            designation_id = self_data.designation_id.id or False            

        if 'market_id' in vals:
            market_id = vals['market_id']
        else:
            market_id = self_data.market_id.id or False            

        if 'region_id' in vals:
            region_id = vals['region_id']
        else:
            region_id = self_data.region_id.id or False            
    #####heirarchy_level is readonly field which'll get update by designation_id
        if 'heirarchy_level' in vals:
            heirarchy_level = vals['heirarchy_level']
        else:    
            heirarchy_level = self_data.heirarchy_level or False
                    
        if 'covering_market_check' in vals:
            covering_market_check = vals['covering_market_check']
        else:
            covering_market_check = self_data.covering_market_check or False
                    
        if 'covering_region_check' in vals:
            covering_region_check = vals['covering_region_check']
        else:
            covering_region_check = self_data.covering_region_check or False


    #####make start date as back date
        if start_date:
            back_date = (datetime.datetime.strptime(start_date, '%Y-%m-%d')) - timedelta(days=1)            

    ######Start Handlings

        dealer_data_ids = self.search(cr, uid, [('dealer_id','=',dealer_id),('start_date','<=',start_date),('end_date','>=',end_date),('covering_str_check','=',False),('covering_market_check','=',False),('covering_region_check','=',False)])
        if len(dealer_data_ids) > 1:
            raise osv.except_osv(('Warning!!'),('Period for which you are updating designation already exist. \nKindly check Designation Tracker record.'))

        desig_data_ids = self.search(cr, uid, [('dealer_id','=',dealer_id),('end_date','>=',start_date), ('start_date','<',end_date),('covering_str_check','=',False),('covering_market_check','=',False),('covering_region_check','=',False)])
        if len(desig_data_ids) > 1:
            raise osv.except_osv(('Warning!!'),('Previous designation exist on this start date. \nKindly check Designation Tracker record.'))
    #####End handling

    #####Start Code By krishna        
        dealer_search = dealer_class.search(cr, uid, [('start_date','<=',start_date),('end_date','>=',end_date),('dealer_id','=',dealer_id)])
        if dealer_search:
            dealer_class.write(cr, uid, dealer_search, {'designation_id':designation_id})

        if dealer_id:
            hr_tab.write(cr, uid, [dealer_id], {'job_id':designation_id})
    #####End Code By krishna

        if isinstance(end_date, (str)):
            check_end_date = (datetime.datetime.strptime(end_date, '%Y-%m-%d'))
        else:
            check_end_date = end_date

        if isinstance(start_date, (str)):
            check_start_date = (datetime.datetime.strptime(start_date, '%Y-%m-%d'))
        else:
            check_start_date = start_date
    #####Start date is greater than end date
        if (check_start_date and check_end_date) and (check_start_date > check_end_date):
                raise osv.except_osv(('Warning!!!'),('End date should be greater than start date. Check dates you have entered.'))

    ######Start Code if employee is not RSM, MM, and DOS - Write Function
        if heirarchy_level not in ('rsm','mm','dos') :
            if dealer_id:
                sap_tracker_id = sap_tracker_obj.search(cr,uid,[('desig_id','=',ids[0])])
                if sap_tracker_id:
                    sap_tracker_obj.unlink(cr,uid,sap_tracker_id[0])

                market_tracker_id = market_tracker_obj.search(cr,uid,[('desig_id','=',ids[0])])
                if market_tracker_id:
                    market_tracker_obj.unlink(cr,uid,market_tracker_id[0])

                region_tracker_id = region_tracker_obj.search(cr,uid,[('desig_id','=',ids[0])])
                if region_tracker_id:
                    region_tracker_obj.unlink(cr,uid,region_tracker_id[0])
            #####check employee is RSM or MM or DOS for given period
            #####if yes, it's raise Warning
            #####else it's update his store/market/region designation in store
                sap_store_ids = desig_track_obj.search(cr, uid, [('dealer_id','=',dealer_id),('id','!=',ids[0]),('end_date','>=',start_date)])
                if len(sap_store_ids)>1:
                    raise osv.except_osv(('Warning!!!'),('Employee previous designation is exist for this period.\nKindly check Designation Tracker record.'))
                else:
                #####Check weather existing employee is store manager of store
                #####Store is search by his latest end date in designation tracker when his designation is RSM
                    
                    ext_desig_track_ids = desig_track_obj.search(cr, uid, [('dealer_id','=',dealer_id),('heirarchy_level','=','rsm')], order='end_date desc')

                    if ext_desig_track_ids:
                        ext_store_id = desig_track_obj.browse(cr,uid,ext_desig_track_ids[0]).store_name.id
                        if ext_store_id:
                            sap_store = self.pool.get('sap.store')
                            ext_store_mgr_id = sap_store.browse(cr, uid, [ext_store_id]).store_mgr_id.id
                            if dealer_id == ext_store_mgr_id:
                                sap_tracker_id = sap_tracker_obj.search(cr,uid,[('desig_id','=',ids[0])])
                                if sap_tracker_id:
                                    sap_tracker_obj.unlink(cr,uid,sap_tracker_id[0])
                                sap_store.write(cr,uid,[ext_store_id],{'store_mgr_id':False})

                    ext_desig_track_ids = desig_track_obj.search(cr, uid, [('covering_str_check','=',True),('dealer_id','=',dealer_id),('heirarchy_level','=','rsm')], order='end_date desc')

                    if ext_desig_track_ids:
                        ext_store_id = desig_track_obj.browse(cr,uid,ext_desig_track_ids[0]).store_name.id
                        if ext_store_id:
                            sap_store = self.pool.get('sap.store')
                            ext_store_mgr_id = sap_store.browse(cr, uid, [ext_store_id]).store_mgr_id.id
                            if dealer_id == ext_store_mgr_id:
                                sap_tracker_id = sap_tracker_obj.search(cr,uid,[('desig_id','=',ids[0])])
                                if sap_tracker_id:
                                    sap_tracker_obj.unlink(cr,uid,sap_tracker_id[0])
                                sap_store.write(cr,uid,[ext_store_id],{'store_mgr_id':False})

                #####Check weather existing employee is Market manager of Market
                #####Market is search by his latest end date in designation tracker when his designation not MM
                    
                    ext_desig_track_ids = desig_track_obj.search(cr, uid, [('dealer_id','=',dealer_id),('heirarchy_level','=','mm')], order='end_date desc')
                    
                    if ext_desig_track_ids:
                        ext_market_id = desig_track_obj.browse(cr,uid,ext_desig_track_ids[0]).market_id.id
                        if ext_market_id:
                            ext_market_mgr_id = market_place_obj.browse(cr, uid, [ext_market_id]).market_manager.id
                            if dealer_id == ext_market_mgr_id:
                                market_tracker_id = market_tracker_obj.search(cr,uid,[('desig_id','=',ids[0])])
                                if market_tracker_id:
                                    market_tracker_obj.unlink(cr,uid,market_tracker_id[0])
                                market_place_obj.write(cr,uid,[ext_market_id],{'market_manager':False})     

                    ext_desig_track_ids = desig_track_obj.search(cr, uid, [('covering_market_check','=',True),('dealer_id','=',dealer_id),('heirarchy_level','=','mm')], order='end_date desc')
                    
                    if ext_desig_track_ids:
                        ext_market_id = desig_track_obj.browse(cr,uid,ext_desig_track_ids[0]).market_id.id
                        if ext_market_id:
                            ext_market_mgr_id = market_place_obj.browse(cr, uid, [ext_market_id]).market_manager.id
                            if dealer_id == ext_market_mgr_id:
                                market_tracker_id = market_tracker_obj.search(cr,uid,[('desig_id','=',ids[0])])
                                if market_tracker_id:
                                    market_tracker_obj.unlink(cr,uid,market_tracker_id[0])
                                market_place_obj.write(cr,uid,[ext_market_id],{'market_manager':False})                                

                #####Check weather existing employee is Sales Director of Region
                #####Region is search by his latest end date in designation tracker when his designation not DOS
                    
                    ext_desig_track_ids = desig_track_obj.search(cr, uid, [('dealer_id','=',dealer_id),('heirarchy_level','=','dos')], order='end_date desc')
                    
                    if ext_desig_track_ids:
                        ext_region_id = desig_track_obj.browse(cr,uid,ext_desig_track_ids[0]).region_id.id
                        if ext_region_id:
                            ext_dos_id = market_regions_obj.browse(cr, uid, [ext_region_id]).sales_director.id
                            if dealer_id == ext_dos_id:
                                region_tracker_id = region_tracker_obj.search(cr,uid,[('desig_id','=',ids[0])])
                                if region_tracker_id:
                                    region_tracker_obj.unlink(cr,uid,region_tracker_id[0])
                                market_regions_obj.write(cr,uid,[ext_region_id],{'sales_director':False})                                                     

                    ext_desig_track_ids = desig_track_obj.search(cr, uid, [('covering_region_check','=',True),('dealer_id','=',dealer_id),('heirarchy_level','=','dos')], order='end_date desc')
                    
                    if ext_desig_track_ids:
                        ext_region_id = desig_track_obj.browse(cr,uid,ext_desig_track_ids[0]).region_id.id
                        if ext_region_id:
                            ext_dos_id = market_regions_obj.browse(cr, uid, [ext_region_id]).sales_director.id
                            if dealer_id == ext_dos_id:
                                region_tracker_id = region_tracker_obj.search(cr,uid,[('desig_id','=',ids[0])])
                                if region_tracker_id:
                                    region_tracker_obj.unlink(cr,uid,region_tracker_id[0])
                                market_regions_obj.write(cr,uid,[ext_region_id],{'sales_director':False})                                
    ######End Code if employee is not RSM, MM, and DOS - Write Function

        res = super(designation_tracker, self).write(cr, uid, ids, vals, context=context)

    #####Start - same manager can not assign for the same store/market/region
        covering_str_check_ids = self.search(cr, uid, [('dealer_id','=',dealer_id),('store_name','!=',False),('covering_str_check','=',False),('end_date','>=',start_date)], order='end_date desc')
        if len(covering_str_check_ids) > 1:
            raise osv.except_osv(('Warning!!!'),('You can not have two base stores assigned within same period.'))
        
        covering_region_check_ids = self.search(cr, uid, [('dealer_id','=',dealer_id),('region_id','!=',False),('covering_region_check','=',False),('end_date','>=',start_date)], order='end_date desc')
        if len(covering_region_check_ids) > 1:
            raise osv.except_osv(('Warning!!!'),('You can not have two base region assigned within same period.'))

        covering_market_check_ids = self.search(cr, uid, [('dealer_id','=',dealer_id),('market_id','!=',False),('covering_market_check','=',False),('end_date','>=',start_date)], order='end_date desc')
        if len(covering_market_check_ids) > 1:
            raise osv.except_osv(('Warning!!!'),('You can not have two base market assigned within same period.'))
    #####End - same manager can not assign for the same store/market/region
    #####Start - Handling if designation already exist

        dealer_data_ids = self.search(cr, uid, [('dealer_id','=',dealer_id),('covering_str_check','=',False),('covering_market_check','=',False),('covering_region_check','=',False),('start_date','<=',start_date),('end_date','>=',end_date)])
        if len(dealer_data_ids) > 1:
            raise osv.except_osv(('Warning!!'),('Period for which you are updating designation already exist.'))

        desig_data_ids = self.search(cr, uid, [('dealer_id','=',dealer_id),('covering_str_check','=',False),('covering_market_check','=',False),('covering_region_check','=',False),('end_date','>=',start_date), ('start_date','<',end_date)])
        if len(desig_data_ids) > 1:
            raise osv.except_osv(('Warning!!'),('Previous designation exist on this start date.'))

    #####End - Handling if designation already exist

    ######Start Code if employee is RSM- Write Function
        if store_name:
            store_name_obj = sap_store.browse(cr,uid,store_name) or False
            if store_name_obj:
                store_sap_number = store_name_obj.sap_number or False
                store_sap_name = store_name_obj.name or False
                if store_sap_number:
                    store_sap_number = str(store_sap_number)
            else:
                store_sap_number = ''
                store_sap_name = ''
            cr.execute('select id from sap_tracker where sap_id = %s and (desig_id != %s or store_mgr_id is null) order by end_date desc'%(str(store_name),str(ids[0])))
            sap_track_ids = map(lambda x: x[0], cr.fetchall())
            # sap_track_ids = sap_tracker_obj.search(cr, uid, [('sap_id','=',),'|',('desig_id','!=',ids[0])],order='end_date desc')

            if sap_track_ids:
                end_date_list = []
        #####Added By Pratik 29 April 2015
                end_date_list = sap_tracker_obj.browse(cr,uid,sap_track_ids[0]).end_date or False
                if isinstance(end_date_list, (str)):
                    end_date_list = (datetime.datetime.strptime(end_date_list, '%Y-%m-%d'))
                else:
                    end_date_list = end_date_list 
                if (check_start_date and end_date_list) and (check_start_date <= end_date_list):
                    if store_sap_name and store_sap_number:
                        raise osv.except_osv(('Warning!!!'),('Store Manager/Sap Tracker Record exists at Store: '+store_sap_name+','+store_sap_number+' for this period.\nPlease assign to a store where Store Manager does not exist.'))
                    else:
                        raise osv.except_osv(('Warning!!!'),('Store Manager/Sap Tracker Record exists at Store for this period..\nPlease assign to a store where Store Manager does not exist.'))
                for sap_track_id in sap_track_ids:
                ##### Validation on start date which have in list
                ##### Don't allow to insert manager if there have mm already in market
                    start_date_list = sap_tracker_obj.browse(cr,uid,sap_track_id).start_date
                    if isinstance(start_date_list, (str)):
                        start_date_list = (datetime.datetime.strptime(start_date_list, '%Y-%m-%d'))
                    else:
                        start_date_list = start_date_list                    
                    if (check_start_date and start_date_list) and (check_start_date <= start_date_list):
                        if store_sap_number:
                            raise osv.except_osv(('Warning!!!'),('Start date should be greater. Check start date in store ',store_sap_number))       
                        else:
                            raise osv.except_osv(('Warning!!!'),('Start date should be greater. Check start date in store.'))

                    if (check_end_date and start_date_list) and (check_end_date <= start_date_list):
                        if store_sap_number:
                            raise osv.except_osv(('Warning!!!'),('End date should be greater. Check start date in store ',store_sap_number))
                        else:
                            raise osv.except_osv(('Warning!!!'),('End date should be greater. Check start date in store.'))

        #####Fetch target store data
        #####Target store - store which is going to be update
            target_store_obj = sap_store.browse(cr,uid,store_name) or False
            target_market_id = target_store_obj.market_id.id or False
            current_store_mgr_id = target_store_obj.store_mgr_id and target_store_obj.store_mgr_id.id or False
            sap_tracker_ids = ''

#        #####If select home base store
#        #####make previous store manager blank and in sap tracker make end date as back date
#        #####Update sap tracker line end date as back date if it's manager
#        #####and it's end date is greater than start date            
#            if covering_str_check == False and store_name:
#                cur_home_store_ids = sap_store.search(cr, uid, [('store_mgr_id','=',dealer_id)])
#                if cur_home_store_ids:                   
#                    sap_tracker_ids = sap_tracker_obj.search(cr, uid, [('sap_id','in',cur_home_store_ids),('store_mgr_id','=',dealer_id)], order = 'end_date desc')
#                    if sap_tracker_ids:
#                        sap_track_end_date = sap_tracker_obj.browse(cr,uid,sap_tracker_ids[0]).end_date
#                        if sap_track_end_date:
#                            sap_track_end_date = datetime.datetime.strptime(sap_track_end_date, '%Y-%m-%d')
#                            if sap_track_end_date > check_start_date:
#                                sap_tracker_obj.write(cr,uid,sap_tracker_ids[0],{'end_date':back_date})                      
#                            sap_store.write(cr, uid, cur_home_store_ids,{'store_mgr_id' : False})
        #####assign manager to sap store
            if store_name and dealer_id:
                sap_store.write(cr, uid, store_name,{'store_mgr_id':dealer_id})

        #####get all sap tracker ids which store and manager are same
            sap_tracker_ids = sap_tracker_obj.search(cr, uid, [('desig_id','=',ids[0]),('sap_id','=',store_name)])
            if sap_tracker_ids:
            #####if record are found it'll update it...
                ext_market_id = sap_store.browse(cr,uid,store_name).market_id.id or False
                sap_tracker_obj.write(cr, uid, sap_tracker_ids, {'sap_id':store_name, 'store_mgr_id':dealer_id,'market_id':ext_market_id,'start_date':start_date,'end_date':end_date,'desig_id':ids[0]})
            else:
            #####if record not found it'll create new line it.
            #####Update sap tracker line
                ext_market_id = sap_store.browse(cr,uid,store_name).market_id.id or False
                ext_sap_tracker = sap_tracker_obj.search(cr,uid,[('sap_id','=',store_name),('desig_id','=',ids[0])])
                if not ext_sap_tracker:
                    sap_tracker_obj.create(cr, uid, {'sap_id':store_name, 'store_mgr_id':dealer_id,'market_id':ext_market_id,'start_date':start_date,'end_date':end_date,'desig_id':ids[0],'store_inactive':False,'store_comments':False,'designation_id':designation_id})

        #####Start Update designation -RSM

        #####Check weather existing employee is Market manager of Market
        #####Market is search by his latest end date in designation tracker when his designation not MM
            
            ext_desig_track_ids = desig_track_obj.search(cr, uid, [('dealer_id','=',dealer_id),('heirarchy_level','=','mm'),('end_date','<=',start_date)], order='end_date desc')
            
            if ext_desig_track_ids:
                ext_market_id = desig_track_obj.browse(cr,uid,ext_desig_track_ids[0]).market_id.id
                if ext_market_id:
                    ext_market_mgr_id = market_place_obj.browse(cr, uid, [ext_market_id]).market_manager.id
                    if dealer_id == ext_market_mgr_id:
                        market_place_obj.write(cr,uid,[ext_market_id],{'market_manager':False})     

        #####Check weather existing employee is Sales Director of Region
        #####Region is search by his latest end date in designation tracker when his designation not DOS
            
            ext_desig_track_ids = desig_track_obj.search(cr, uid, [('dealer_id','=',dealer_id),('heirarchy_level','=','dos'),('end_date','<=',start_date)], order='end_date desc')
            
            if ext_desig_track_ids:
                ext_region_id = desig_track_obj.browse(cr,uid,ext_desig_track_ids[0]).region_id.id
                if ext_region_id:
                    ext_dos_id = market_regions_obj.browse(cr, uid, [ext_region_id]).sales_director.id
                    if ext_dos_id:
                        if dealer_id == ext_dos_id:
                            market_regions_obj.write(cr,uid,[ext_region_id],{'sales_director':False})                         
    #####End Update designation - RSM               
    #####Start Delete from market and region - 25/03/2015
    #####Delete from Market Manager
            ext_mm_ids = market_place_obj.search(cr, uid, [('market_manager','=',dealer_id)])
            if ext_mm_ids:
                for ext_mm_id in ext_mm_ids:
                    market_place_obj.write(cr,uid,[ext_mm_id],{'market_manager':False})
    #####Delete from Market Tracker
            market_tracker_ids = market_tracker_obj.search(cr,uid, [('desig_id','=',ids),])
            if market_tracker_ids:
                for market_tracker_id in market_tracker_ids:
                    market_tracker_obj.unlink(cr,uid,market_tracker_id)
    #####Delete from Region Sales Director
            ext_dos_ids = market_regions_obj.search(cr, uid, [('sales_director','=',dealer_id)])
            if ext_dos_ids:
                for ext_dos_id in ext_dos_ids:
                    market_regions_obj.write(cr,uid,[ext_dos_id],{'sales_director':False})              
    #####Delete from region tracker
            region_tracker_ids = region_tracker_obj.search(cr,uid, [('desig_id','=',ids),])
            if region_tracker_ids:
                for region_tracker_id in region_tracker_ids:
                    region_tracker_obj.unlink(cr,uid,region_tracker_id)
    ######End Code if employee is RSM - Write Function

    #####Start code for MM
        if market_id and heirarchy_level == 'mm':
            market_id_obj = market_place_obj.browse(cr,uid,market_id)
            market_name = market_id_obj.name
            target_market_region = market_id_obj.region_market_id.id
            target_market_manager = market_id_obj.market_manager.id


            market_tracker_ids = ''
            if market_id and ids:
                cr.execute('select id from market_tracker where market_id = %s and (desig_id != %s or desig_id is null) order by end_date desc;'%(str(market_id),str(ids[0])))
                market_tracker_ids = map(lambda x: x[0], cr.fetchall())
            logger.info("market_tracker_ids-------------------------------------%s"%(market_tracker_ids))    
            if market_tracker_ids:
            #####Added By Pratik 29 April 2015
                end_date_list = market_tracker_obj.browse(cr,uid,market_tracker_ids[0]).end_date
                if isinstance(end_date_list, (str)):
                    end_date_list = (datetime.datetime.strptime(end_date_list, '%Y-%m-%d'))
                else:
                    end_date_list = end_date_list

                if (check_start_date and end_date_list) and (check_start_date <= end_date_list):
                    if market_name:
                        raise osv.except_osv(('Warning!!!'),('Market Manager/Market Tracker Record exists at market:: '+market_name+'\nPlease assign to a store where Market Manager does not exist.'))
                    else:
                        raise osv.except_osv(('Warning!!!'),('Market Manager/Market Tracker Record exists at market.\nPlease assign to a store where Market Manager does not exist.'))
                for market_tracker_id in market_tracker_ids:
                    start_date_list = market_tracker_obj.browse(cr,uid,market_tracker_id).start_date or False

                    if start_date_list and isinstance(start_date_list, (str)):
                        start_date_list = (datetime.datetime.strptime(start_date_list, '%Y-%m-%d'))
                    else:
                        start_date_list = start_date_list                    

                    if (check_start_date and start_date_list) and (check_start_date <= start_date_list):
                        market_name = market_place_obj.browse(cr,uid,market_id).name
                        raise osv.except_osv(('Warning!!!'),('Start date shoud be greater. Check start date in market - '+market_name))       
                    if (check_end_date and start_date_list) and (check_end_date <= start_date_list):
                       raise osv.except_osv(('Warning!!!'),('End date shoud be greater. Check start date in market - '+market_name))  

            if dealer_id:
                sap_store_ids = desig_track_obj.search(cr, uid, [('dealer_id','=',dealer_id),('end_date','>=',start_date),('covering_str_check','=',False), ('covering_market_check','=',False), ('covering_region_check','=',False)])
                if len(sap_store_ids)>1:
                    raise osv.except_osv(('Warning!!!'),('Employee previous designation is exist for this period.'))
                else:
                #####Update current manager as MM in target market
                    if dealer_id and market_id:
                        market_place_obj.write(cr,uid,[market_id],{'market_manager':dealer_id})
                #####if market tracker line exist then it'll update it else create new market tracker line

                    ext_market_tracker_id = market_tracker_obj.search(cr,uid,[('desig_id','=',ids[0])])
                    if ext_market_tracker_id:
                        market_tracker_obj.write(cr,uid,ext_market_tracker_id,{'region_market_id':target_market_region, 'market_manager':dealer_id, 'market_id':market_id, 'end_date': end_date, 'start_date': start_date, 'desig_id':ids[0],'designation_id':designation_id})
                    else:
                        market_tracker_obj.create(cr,uid,{'region_market_id':target_market_region, 'market_manager':dealer_id, 'market_id':market_id, 'end_date': end_date, 'start_date': start_date, 'desig_id':ids[0],'designation_id':designation_id})
            
            #####Start Update Designation - MM

            #####Check weather existing employee is Store Manager of Store
            #####Store is search by his latest end date in designation tracker when his designation not RSM

                ext_desig_track_ids = desig_track_obj.search(cr, uid, [('dealer_id','=',dealer_id),('heirarchy_level','=','rsm'),('end_date','<=',start_date)], order='end_date desc')

                if ext_desig_track_ids:
                    ext_store_id = desig_track_obj.browse(cr,uid,ext_desig_track_ids[0]).store_name.id
                    if ext_store_id:
                        sap_store = self.pool.get('sap.store')
                        ext_store_mgr_id = sap_store.browse(cr, uid, [ext_store_id]).store_mgr_id.id
                        if dealer_id == ext_store_mgr_id:
                            sap_store.write(cr,uid,[ext_store_id],{'store_mgr_id':False})
            #####Check weather existing employee is Sales Director of Region
            #####Region is search by his latest end date in designation tracker when his designation not DOS
                
                ext_desig_track_ids = desig_track_obj.search(cr, uid, [('dealer_id','=',dealer_id),('heirarchy_level','=','dos'),('end_date','<=',start_date)], order='end_date desc')
                
                if ext_desig_track_ids:
                    ext_region_id = desig_track_obj.browse(cr,uid,ext_desig_track_ids[0]).region_id.id
                    if ext_region_id:
                        ext_dos_id = market_regions_obj.browse(cr, uid, [ext_region_id]).sales_director.id
                        if dealer_id == ext_dos_id:
                            market_regions_obj.write(cr,uid,[ext_region_id],{'sales_director':False})                 
        #####Start Delete from sap store and market - 25/03/2015        
                ext_rsm_ids = sap_store.search(cr, uid, [('store_mgr_id','=',dealer_id)])
                if ext_rsm_ids:
                    for ext_rsm_id in ext_rsm_ids:
                        sap_store.write(cr,uid,[ext_rsm_id],{'store_mgr_id':False})
                sap_tracker_ids = sap_tracker_obj.search(cr,uid, [('desig_id','=',ids),])
                if sap_tracker_ids:
                    for sap_tracker_id in sap_tracker_ids:
                        sap_tracker_obj.unlink(cr,uid,sap_tracker_id) 
                ext_dos_ids = market_regions_obj.search(cr, uid, [('sales_director','=',dealer_id)])
                if ext_dos_ids:
                    for ext_dos_id in ext_dos_ids:
                        market_regions_obj.write(cr,uid,[ext_dos_id],{'sales_director':False})
                region_tracker_ids = region_tracker_obj.search(cr,uid, [('desig_id','=',ids),])
                if region_tracker_ids:
                    for region_tracker_id in region_tracker_ids:
                        region_tracker_obj.unlink(cr,uid,region_tracker_id) 
        #####End Update Designation - MM                           
        #####Start patch code for updating market manager from market
            if market_id and dealer_id:
                market_place_ids = market_place_obj.search(cr,uid,[('market_manager','=',dealer_id),('id','!=',market_id)])
                if market_place_ids:
                    for market_place_id in market_place_ids:
                        market_place_obj.write(cr,uid,[market_place_id],{'market_manager':False})
        #####End patch code for updating market manager from market

    #####End code for MM                 

    #####Start functionality for DOS
        if heirarchy_level == 'dos' and 'region_id':
            region_id_obj = market_regions_obj.browse(cr,uid,region_id)
            region_name = region_id_obj.name
            target_region_dos = region_id_obj.sales_director.id or False

            emp_no = hr_tab.browse(cr,uid,dealer_id).emp_no or False
            target_company_id = False

            if emp_no:
                res_users_id = res_users_obj.search(cr,uid,[('login','=',emp_no)])
                if res_users_id:
                    target_company_id = res_users_obj.browse(cr,uid,res_users_id[0]).company_id.id or False
                    
            if region_id and ids:
                cr.execute('select id from region_tracker where region_id = %s and (desig_id != %s or desig_id is null) order by end_date desc;'%(str(region_id),str(ids[0])))
                region_tracker_ids = map(lambda x: x[0], cr.fetchall())
            else:
                region_tracker_ids = ''
            # region_tracker_ids = region_tracker_obj.search(cr, uid, [('region_id','=',region_id),('desig_id','!=',ids[0])], order = 'end_date desc')

            if region_tracker_ids:
#####Added By Pratik 29 April 2015
                end_date_list = region_tracker_obj.browse(cr,uid,region_tracker_ids[0]).end_date
                if end_date_list and isinstance(end_date_list, (str)):
                    end_date_list = (datetime.datetime.strptime(end_date_list, '%Y-%m-%d'))
                else:
                    end_date_list = end_date_list   
                if (end_date_list and check_start_date) and (check_start_date <= end_date_list):
                    if region_name:
                        raise osv.except_osv(('Warning!!!'),('Director of Sales/Region Tracker record exists at region: '+region_name+'\nPlease assign to a region where Director of Sales does not exist.'))
                    else:
                        raise osv.except_osv(('Warning!!!'),('Director of Sales exists/Region Tracker record at region.\nPlease assign to a region where Director of Sales does not exist.'))
                for region_tracker_id in region_tracker_ids:
                    start_date_list = region_tracker_obj.browse(cr,uid,region_tracker_id).start_date
                    if isinstance(start_date_list, (str)):
                        start_date_list = (datetime.datetime.strptime(start_date_list, '%Y-%m-%d'))
                    else:
                        start_date_list = start_date_list

                    if (check_start_date and start_date_list) and (check_start_date <= start_date_list):
                        raise osv.except_osv(('Warning!!!'),('Start date shoud be greater. Check start date in market - '+region_name))       
                    if (check_end_date and start_date_list) and (check_end_date <= start_date_list):
                       raise osv.except_osv(('Warning!!!'),('End date shoud be greater. Check start date in market - '+region_name))  

        #####Target Region data
            
        #####Update current manager as DOS in target Region
            if region_id and dealer_id:
                market_regions_obj.write(cr,uid,[region_id],{'sales_director':dealer_id})

        #####if Region tracker line exist then it'll update it else create new region tracker line
            ext_region_tracker_id = region_tracker_obj.search(cr,uid,[('desig_id','=',ids[0])])
            if ext_region_tracker_id:
                region_tracker_obj.write(cr,uid,ext_region_tracker_id[0],{'company_id':target_company_id, 'sales_director':dealer_id, 'region_id':region_id, 'end_date': end_date, 'start_date': start_date, 'desig_id':ids[0],'designation_id':designation_id})
            else:
                region_tracker_ids = region_tracker_obj.search(cr,uid,[('desig_id','=',ids[0]),('region_id','=',region_id)])
                if not region_tracker_ids:
                    region_tracker_obj.create(cr,uid,{'company_id':target_company_id, 'sales_director':dealer_id, 'region_id':region_id, 'end_date': end_date, 'start_date': start_date, 'desig_id':ids[0],'designation_id':designation_id})

        #####Start Update Designation - DOS 
                    
        #####Check weather existing employee is Store Manager of Store
        #####Store is search by his latest end date in designation tracker when his designation not RSM

            ext_desig_track_ids = desig_track_obj.search(cr, uid, [('dealer_id','=',dealer_id),('heirarchy_level','=','rsm'),('end_date','<=',start_date)], order='end_date desc')

            if ext_desig_track_ids:
                ext_store_id = desig_track_obj.browse(cr,uid,ext_desig_track_ids[0]).store_name.id
                if ext_store_id:
                    sap_store = self.pool.get('sap.store')
                    ext_store_mgr_id = sap_store.browse(cr, uid, [ext_store_id]).store_mgr_id.id
                    if dealer_id == ext_store_mgr_id:
                        sap_store.write(cr,uid,[ext_store_id],{'store_mgr_id':False})

        #####Check weather existing employee is Market manager of Market
        #####Market is search by his latest end date in designation tracker when his designation not MM
            
            ext_desig_track_ids = desig_track_obj.search(cr, uid, [('dealer_id','=',dealer_id),('heirarchy_level','=','mm'),('end_date','<=',start_date)], order='end_date desc')
            
            if ext_desig_track_ids:
                ext_market_id = desig_track_obj.browse(cr,uid,ext_desig_track_ids[0]).market_id.id
                if ext_market_id:
                    ext_market_mgr_id = market_place_obj.browse(cr, uid, [ext_market_id]).market_manager.id
                    if dealer_id == ext_market_mgr_id:
                        market_place_obj.write(cr,uid,[ext_market_id],{'market_manager':False})             
        #####End Update Designation - DOS
            ext_mm_ids = market_place_obj.search(cr, uid, [('market_manager','=',dealer_id)])
            if ext_mm_ids:
                for ext_mm_id in ext_mm_ids:
                    market_place_obj.write(cr,uid,[ext_mm_id],{'market_manager':False})
        #####Delete from market tracker
            market_tracker_ids = market_tracker_obj.search(cr,uid, [('desig_id','=',ids),])
            if market_tracker_ids:
                for market_tracker_id in market_tracker_ids:
                    market_tracker_obj.unlink(cr,uid,market_tracker_id)
                    ext_rsm_ids = sap_store.search(cr, uid, [('store_mgr_id','=',dealer_id)])
                    if ext_rsm_ids:
                        for ext_rsm_id in ext_rsm_ids:
                            sap_store.write(cr,uid,[ext_rsm_id],{'store_mgr_id':False})
        #####Delete From SAP Tracker
            sap_tracker_ids = sap_tracker_obj.search(cr,uid, [('desig_id','=',ids),])
            if sap_tracker_ids:
                for sap_tracker_id in sap_tracker_ids:
                    sap_tracker_obj.unlink(cr,uid,sap_tracker_id) 
        #####Start patch code for updating Sale director manager from region
            if region_id and dealer_id:
                market_regions_ids = market_regions_obj.search(cr,uid,[('sales_director','=',dealer_id),('id','!=',region_id)])

                if market_regions_ids:
                    for market_regions_id in market_regions_ids:
                        market_regions_obj.write(cr,uid,[market_regions_id],{'sales_director':False})
        #####End patch code for updating Sale director manager from region

    #####End functionality for DOS    

    
    #####Start Covering Store Newly developed Functionality - write Function
        if dealer_id and not covering_str_check:
            sap_store_ids = sap_store.search(cr,uid,[('store_mgr_id','=',dealer_id)])
            cr.execute('select store_id from hr_id_store_id where hr_id = %s'%(dealer_id))
            hr_id_store_id = map(lambda x: x[0], cr.fetchall())

            if hr_id_store_id and sap_store_ids:
                delete_records = list(set(hr_id_store_id) - set(sap_store_ids))
                insert_records = list(set(sap_store_ids) - set(hr_id_store_id))

                if delete_records:
                    for delete_record in delete_records:
                        cr.execute('delete from hr_id_store_id where hr_id = %s and store_id = %s',(dealer_id,delete_record))
                if insert_records:
                    for insert_record in insert_records:
                        cr.execute('select * from hr_id_store_id where hr_id = %s and store_id = %s',(dealer_id,insert_record))
                        ext_hr_id_store_id = map(lambda x: x[0], cr.fetchall())
                        if not ext_hr_id_store_id:
                            cr.execute('insert into hr_id_store_id (hr_id, store_id) values(%s,%s)',(dealer_id,insert_record))
        #####If there have sap_store_ids only but there is no data will presnt in covering store
        #####It'll insert new data into covering store
            elif sap_store_ids:
                for sap_store_id in sap_store_ids:
                    cr.execute('select * from hr_id_store_id where hr_id = %s and region_id = %s',(dealer_id,sap_store_id))
                    ext_hr_id_store_id = map(lambda x: x[0], cr.fetchall())
                    if not ext_hr_id_store_id:
                        cr.execute('insert into hr_id_store_id (hr_id, region_id) values(%s,%s)',(dealer_id,sap_store_id))            
        #####If there are records in covering store
        #####but currently that employee is not a RSM of any store
        #####Delete such records from covering store
            else:
                cr.execute('delete from hr_id_store_id where hr_id = %s',(dealer_id,))                            
    #####End Covering Store Newly developed Functionality - write Function  

    #####Start Covering Market Functionality - write Function
        #####Get market id in which current employee is assigned as manager    
            market_ids = market_place_obj.search(cr,uid,[('market_manager','=',dealer_id)])
        #####Get the data of covering market table
            cr.execute('select market_id from hr_id_market_id where hr_id = %s'%(dealer_id))
            hr_id_market_id = map(lambda x: x[0], cr.fetchall())
        #####If there have a market id and covering market data
        #####It'll check covering market data with market ids and delete unwanted one 
        #####as well as insert new one   
            if hr_id_market_id and market_ids:
                delete_records = list(set(hr_id_market_id) - set(market_ids))
                insert_records = list(set(market_ids) - set(hr_id_market_id))
            #####if there have any missed match data
            #####It will delete it from covering market
            #####and insert new one in covering market
                if delete_records:
                    for delete_record in delete_records:
                        cr.execute('delete from hr_id_market_id where hr_id = %s and market_id = %s',(dealer_id,delete_record))
                if insert_records:
                    for insert_record in insert_records:
                        cr.execute('select * from hr_id_market_id where hr_id = %s and market_id = %s',(dealer_id,insert_record))
                        ext_hr_id_market_id = map(lambda x: x[0], cr.fetchall())
                        if not ext_hr_id_market_id:
                            cr.execute('insert into hr_id_market_id (hr_id, market_id) values(%s,%s)',(dealer_id,insert_record))
        #####If there have market_ids only but there is no data will presnt in covering market
        #####It'll insert new data into covering market
            elif market_ids:
                for market_id in market_ids:
                    cr.execute('select * from hr_id_market_id where hr_id = %s and market_id = %s',(dealer_id,market_id))
                    ext_hr_id_market_id = map(lambda x: x[0], cr.fetchall())
                    if not ext_hr_id_market_id:
                        cr.execute('insert into hr_id_market_id (hr_id, market_id) values(%s,%s)',(dealer_id,market_id))            
        #####If there are records in covering market
        #####but currently that employee is not a MM of any market
        #####Delete such records from covering market
            else:
                cr.execute('delete from hr_id_market_id where hr_id = %s',(dealer_id,))
    #####End Covering Market Functionality - write Function

    #####Start Covering Region Functionality - write Function
        #####Get region id in which current employee is assigned as manager
            region_ids = market_regions_obj.search(cr,uid,[('sales_director','=',dealer_id)])
        #####Get the data of covering region table
            cr.execute('select region_id from hr_id_region_id where hr_id = %s'%(dealer_id))
            hr_id_region_id = map(lambda x: x[0], cr.fetchall())
        #####If there have a region id and covering market data
        #####It'll check covering region data with region ids and delete unwanted one
        #####as well as insert new one   
            if hr_id_region_id and region_ids:
                delete_records = list(set(hr_id_region_id) - set(region_ids))
                insert_records = list(set(region_ids) - set(hr_id_region_id))
            #####if there have any missed match data
            #####It will delete it from covering region
            #####and insert new one in covering region
                if delete_records:
                    for delete_record in delete_records:
                        cr.execute('delete from hr_id_region_id where hr_id = %s and region_id = %s',(dealer_id,delete_record))
                if insert_records:
                    for insert_record in insert_records:
                        cr.execute('select * from hr_id_region_id where hr_id = %s and region_id = %s',(dealer_id,insert_record))
                        ext_hr_id_region_id = map(lambda x: x[0], cr.fetchall())
                        if not ext_hr_id_region_id:
                            cr.execute('insert into hr_id_region_id (hr_id, region_id) values(%s,%s)',(dealer_id,insert_record))
        #####If there have region_id only but there is no data will presnt in covering region
        #####It'll insert new data into covering region
            elif region_ids:
                for region_id in region_ids:
                    cr.execute('select * from hr_id_region_id where hr_id = %s and region_id = %s',(dealer_id,region_id))
                    ext_hr_id_region_id = map(lambda x: x[0], cr.fetchall())
                    if not ext_hr_id_region_id:
                        cr.execute('insert into hr_id_region_id (hr_id, region_id) values(%s,%s)',(dealer_id,region_id))            
        #####If there are records in covering region
        #####but currently that employee is not a DOS of any region
        #####Delete such records from covering region
            else:
                cr.execute('delete from hr_id_region_id where hr_id = %s',(dealer_id,))
    #####End Covering Region Functionality - write Function  

    #####Start patch for covering_str_check
    #####If designation is not rsm it'll make covering_str_check False
        if heirarchy_level != 'rsm' and covering_str_check == True:
            self.write(cr,uid,ids,{'covering_str_check':False})
        if heirarchy_level != 'mm' and covering_market_check == True:
            self.write(cr,uid,ids,{'covering_market_check':False})
        if heirarchy_level != 'dos' and covering_region_check == True:
            self.write(cr,uid,ids,{'covering_region_check':False})
    #####End patch for covering_str_check


    #####If dealer_id is MM or DOS then make it's Home base store as corporate
        market_mgr_ids = market_place_obj.search(cr,uid,[('market_manager','=',dealer_id)]) or False
        region_mgr_ids = market_regions_obj.search(cr,uid,[('sales_director','=',dealer_id)]) or False
        
        if market_mgr_ids:
            if len(market_mgr_ids)>0:
                sap_store_id = sap_store.search(cr,uid,[('sap_number','=','1')]) or False
                if sap_store_id:
                    hr_tab.write(cr,uid,dealer_id,{'store_id':sap_store_id[0]})

        elif region_mgr_ids:
            if len(region_mgr_ids)>0:
                sap_store_id = sap_store.search(cr,uid,[('sap_number','=','1')]) or False
                if sap_store_id:                
                    hr_tab.write(cr,uid,dealer_id,{'store_id':sap_store_id[0]})
    #####End If dealer_id is MM or DOS then make it's Home base store as corporate

        if dealer_id:
            ext_desig_ids = self.search(cr, uid, [('dealer_id','=',dealer_id)], order='end_date desc')
            if ext_desig_ids:
                ext_designation_id = self.browse(cr,uid,ext_desig_ids[0]).designation_id.id or False
                heirarchy_level_value = self.browse(cr,uid,ext_desig_ids[0]).heirarchy_level or False
                if heirarchy_level_value and heirarchy_level_value == 'rsm':
                    store_name_value = self.browse(cr,uid,ext_desig_ids[0]).store_name.id or False
                else:
                    store_name_value = ''
                if ext_designation_id and store_name_value:
                    hr_tab.write(cr, uid, dealer_id, {'store_id':store_name_value, 'job_id':ext_designation_id})
                elif ext_designation_id:
                    hr_tab.write(cr, uid, dealer_id, {'job_id':ext_designation_id})
  
    #####Start Assign Access rights - Write Function
    #####Dont't forget to create object of class res_users,hr_job,
        if dealer_id and end_date:
            emp_no = hr_tab.browse(cr,uid,dealer_id).emp_no or False
            emp_active = hr_tab.browse(cr,uid,dealer_id).active or False
            res_users_ids = res_users_obj.search(cr,uid,[('login','=',emp_no)])
            if not res_users_ids:
                cr.execute('select id from res_users where login = %s',(emp_no,))
                res_users_ids = map(lambda x: x[0], cr.fetchall())
            current_date = datetime.datetime.now(pytz.timezone('US/Mountain')) 
        #####search designation tracker id for current employee where start date is greater than current date
            cr_desig_track_ids = desig_track_obj.search(cr, uid, [('dealer_id','=',dealer_id),('end_date','>=',start_date)], order='end_date desc')
            if cr_desig_track_ids:
                if len(cr_desig_track_ids) <= 1:
                #####Get designation of the current employee
                    cr_designation_id = self.browse(cr,uid,cr_desig_track_ids[0]).designation_id.id or False
                    if cr_designation_id:
                    #####Check weather that designation have assigned access groups
                        cr.execute('select gid from job_res_group_rel where jid = %s'%(cr_designation_id))
                        cr_access_groups_ids = map(lambda x: x[0], cr.fetchall())
                        logger.error("For Group id %s"%(cr_access_groups_ids))

                        if cr_access_groups_ids:
                            if res_users_ids:
                            #####Get access groups ids of that designation i.e. employee current designation
                                cr.execute('select gid from res_groups_users_rel where uid = %s'%(res_users_ids[0]))
                                res_groups_users_rel_ids = map(lambda x: x[0], cr.fetchall())
                            #####If employee have assigned access groups
                            #####then it's delete that access groups first and assign current designation's access groups                            
                                if len(res_groups_users_rel_ids)>0:
                                    cr.execute('delete from res_groups_users_rel where uid = %s'%(res_users_ids[0]))  
                                    if emp_active == True:
                                        for cr_access_groups_id in cr_access_groups_ids:
                                            cr.execute('insert into res_groups_users_rel (uid, gid) values(%s,%s)'%(res_users_ids[0],cr_access_groups_id))
                                            logger.info("For external employee id %s access group %s assigned"%(dealer_id, cr_access_groups_id))
                                else:
                                    if emp_active == True:
                                        for cr_access_groups_id in cr_access_groups_ids:
                                            cr.execute('insert into res_groups_users_rel (uid, gid) values(%s,%s)'%(res_users_ids[0],cr_access_groups_id))
                                            logger.info("For external employee id %s access group %s assigned"%(dealer_id, cr_access_groups_id))
                            else:
                                raise osv.except_osv(('Warning!!!'),('Employee is not active in res_users'))   
                    #####If employee does not have access groups
                    #####assign current designation's access groups                            
                        else:
                            raise osv.except_osv(('Warning!!!'),('For this job designation Access group is not assigned. Kindly assign access group first in Job Position and then try.'))   

    #####Start Update res_user for jasper

    #####update latest designation in job title

        values = {}
        emp_no = hr_tab.browse(cr,uid,dealer_id).emp_no or False
        if emp_no:
            res_users_id = res_users_obj.search(cr,uid,[('login','=',emp_no)])
            if res_users_id:
                values.update({'login':emp_no})
                res_users_obj.write(cr,uid,res_users_id,values)

        return res

    def unlink(self, cr, uid, ids, context=None):
        
        res = False
##### Start Code By Pratik
        desig_track_obj = self.pool.get('designation.tracker')

        sap_store = self.pool.get('sap.store')
        sap_tracker_obj = self.pool.get('sap.tracker')

        market_tracker_obj = self.pool.get('market.tracker')
        market_place_obj = self.pool.get('market.place')

        region_tracker_obj = self.pool.get('region.tracker')
        market_regions_obj = self.pool.get('market.regions')

        hr_tab = self.pool.get('hr.employee')
        res_users_obj = self.pool.get('res.users')

        end_date = self.browse(cr,uid,ids[0]).end_date
        start_date = self.browse(cr,uid,ids[0]).start_date
        covering_str_check = self.browse(cr,uid,ids[0]).covering_str_check
        covering_market_check = self.browse(cr,uid,ids[0]).covering_market_check
        covering_region_check = self.browse(cr,uid,ids[0]).covering_region_check
        dealer_id = self.browse(cr,uid,ids[0]).dealer_id.id
        store_name = self.browse(cr,uid,ids[0]).store_name.id

    ##### Start Code By Krishna   
        hr_obj = self.pool.get('hr.employee')
        user_obj = self.pool.get('res.users')
        designation_id = False
        self_record_data = self.browse(cr, uid, ids[0])
        del_hr_id = self_record_data.dealer_id.id or False
        user_id = self_record_data.dealer_id.user_id.id or False

        if del_hr_id:
            dealer_all_ids = self.search(cr, uid, [('dealer_id','=',del_hr_id)])
        else:
            dealer_all_ids = []
        if len(dealer_all_ids) > 1:
            dealer_date_search = self.search(cr, uid, [('dealer_id','=',del_hr_id)], order='end_date')
            for dealer_date_search_id in dealer_date_search:
                dealer_current_data = self.browse(cr, uid, dealer_date_search_id)
                designation_id = dealer_current_data.designation_id.id
            hr_obj.write(cr, uid, [del_hr_id], {'job_id':designation_id})
    ##### End Code By Krishna
    #####Start For RSM
        sap_tracker_ids = sap_tracker_obj.search(cr, uid, [('desig_id','=',ids[0])])
        if sap_tracker_ids:
            for sap_tracker_id in sap_tracker_ids:             
                tracker_store_id = sap_tracker_obj.browse(cr,uid,sap_tracker_id).sap_id.id
                if tracker_store_id:
                    sap_mgr_id = sap_store.browse(cr,uid,tracker_store_id).store_mgr_id.id
                    if sap_mgr_id == dealer_id:
                        sap_store.write(cr,uid,[tracker_store_id],{'store_mgr_id': False})
                sap_tracker_obj.unlink(cr, uid, sap_tracker_id)
    #####End For RSM

    #####Start For MM
        market_tracker_ids = market_tracker_obj.search(cr, uid, [('desig_id','=',ids[0])])
        if market_tracker_ids:
            for market_tracker_id in market_tracker_ids:
                tracker_market_id = market_tracker_obj.browse(cr,uid,market_tracker_id).market_id.id
                if tracker_market_id:
                    market_mgr_id = market_place_obj.browse(cr,uid,tracker_market_id).market_manager.id
                    if market_mgr_id == dealer_id:
                        market_place_obj.write(cr,uid,[tracker_market_id],{'market_manager': False})                       
                market_tracker_obj.unlink(cr, uid, market_tracker_id)
    #####End For MM

    #####Start For DOS
        region_tracker_ids = region_tracker_obj.search(cr, uid, [('desig_id','=',ids[0])])
        if region_tracker_ids:
            for region_tracker_id in region_tracker_ids:
                tracker_region_id = region_tracker_obj.browse(cr,uid,region_tracker_id).region_id.id
                if tracker_region_id:
                    region_mgr_id = market_regions_obj.browse(cr,uid,tracker_region_id).sales_director.id
                    if region_mgr_id == dealer_id:
                        market_regions_obj.write(cr,uid,[tracker_region_id],{'sales_director': False})                        
                region_tracker_obj.unlink(cr, uid, region_tracker_id)

    #####End For DOS
    
    #####Start Covering Store Newly developed Functionality - unlink Function
        if dealer_id and not covering_str_check:
            
            sap_store_ids = sap_store.search(cr,uid,[('store_mgr_id','=',dealer_id)])
            cr.execute('select store_id from hr_id_store_id where hr_id = %s'%(dealer_id))
            hr_id_store_id = map(lambda x: x[0], cr.fetchall())
            if hr_id_store_id and sap_store_ids:
                delete_records = list(set(hr_id_store_id) - set(sap_store_ids))
                
                if delete_records:
                    for delete_record in delete_records:
                        cr.execute('delete from hr_id_store_id where hr_id = %s and store_id = %s',(dealer_id,delete_record))                
        #####If there are records in covering store
        #####but currently that employee is not a RSM of any store
        #####Delete such records from covering store
            else:
                cr.execute('delete from hr_id_store_id where hr_id = %s',(dealer_id,)) 
                
    #####End Covering Store Newly developed Functionality - unlink Function

    #####Start Covering Market Functionality - unlink Function
        if dealer_id and not covering_market_check:
        #####Get market id in which current employee is assigned as manager    
            market_ids = market_place_obj.search(cr,uid,[('market_manager','=',dealer_id)])
        #####Get the data of covering market table
            cr.execute('select market_id from hr_id_market_id where hr_id = %s'%(dealer_id))
            hr_id_market_id = map(lambda x: x[0], cr.fetchall())
        #####If there have a market id and covering market data
        #####It'll check covering market data with market ids and delete unwanted one 
        #####as well as insert new one   
            if hr_id_market_id and market_ids:
                delete_records = list(set(hr_id_market_id) - set(market_ids))
                
            #####if there have any missed match data
            #####It will delete it from covering market
            #####and insert new one in covering market
                if delete_records:
                    for delete_record in delete_records:
                        cr.execute('delete from hr_id_market_id where hr_id = %s and market_id = %s',(dealer_id,delete_record))
        #####If there are records in covering market
        #####but currently that employee is not a MM of any market
        #####Delete such records from covering market
            else:
                cr.execute('delete from hr_id_market_id where hr_id = %s',(dealer_id,))
    #####End Covering Market Functionality - unlink Function

    #####Start Covering Region Functionality - unlink Function
        if dealer_id and not covering_region_check:
        #####Get region id in which current employee is assigned as manager
            region_ids = market_regions_obj.search(cr,uid,[('sales_director','=',dealer_id)])
        #####Get the data of covering region table
            cr.execute('select region_id from hr_id_region_id where hr_id = %s'%(dealer_id))
            hr_id_region_id = map(lambda x: x[0], cr.fetchall())
        #####If there have a region id and covering market data
        #####It'll check covering region data with region ids and delete unwanted one
        #####as well as insert new one 
            if hr_id_region_id and region_ids:
                delete_records = list(set(hr_id_region_id) - set(region_ids))                
            #####if there have any missed match data
            #####It will delete it from covering region
            #####and insert new one in covering region
                if delete_records:
                    for delete_record in delete_records:
                        cr.execute('delete from hr_id_region_id where hr_id = %s and region_id = %s',(dealer_id,delete_record))
        #####If there are records in covering region
        #####but currently that employee is not a DOS of any region
        #####Delete such records from covering region
            else:
                cr.execute('delete from hr_id_region_id where hr_id = %s',(dealer_id,))    
    #####End Covering Region Functionality - unlink Function                

        if dealer_id:
            ext_desig_ids = self.search(cr, uid, [('dealer_id','=',dealer_id),('id','!=',ids[0])], order='end_date desc')
            if ext_desig_ids:
                ext_designation_id = self.browse(cr,uid,ext_desig_ids[0]).designation_id.id or False
                heirarchy_level_value = self.browse(cr,uid,ext_desig_ids[0]).heirarchy_level or False
                if heirarchy_level_value and heirarchy_level_value == 'rsm':
                    store_name_value = self.browse(cr,uid,ext_desig_ids[0]).store_name.id or False
                else:
                    store_name_value = ''
                if ext_designation_id and store_name_value:
                    hr_tab.write(cr, uid, dealer_id, {'store_id':store_name_value, 'job_id':ext_designation_id})
                elif ext_designation_id:
                    hr_tab.write(cr, uid, dealer_id, {'job_id':ext_designation_id})
##### End Code By Pratik     

    #####Commented By Krishna            
            # else:
            #     raise osv.except_osv(('Alert!!'),('Please provide future end date for previous designation record before deleting current one.'))
        # else:
        #     hr_obj.write(cr, uid, [del_hr_id], {'job_id':False})
    #####End Commented By Krishna


    #####Start Assign Access rights - Unlink Function
        if dealer_id and end_date:
            desig_track_obj = self.pool.get('designation.tracker')
            emp_no = hr_tab.browse(cr,uid,dealer_id).emp_no or False
            emp_active = hr_tab.browse(cr,uid,dealer_id).active or False
            res_users_ids = res_users_obj.search(cr,uid,[('login','=',emp_no)])
            if not res_users_ids:
                cr.execute('select id from res_users where login = %s',(emp_no,))
                res_users_ids = map(lambda x: x[0], cr.fetchall())      
            current_date = datetime.datetime.now(pytz.timezone('US/Mountain')) 
            cr_desig_track_ids = desig_track_obj.search(cr, uid, [('dealer_id','=',dealer_id),('id','!=',ids[0])], order='end_date desc')
            if cr_desig_track_ids:
                if len(cr_desig_track_ids) >= 0:
                #####Get designation of the current employee
                    cr_designation_id = self.browse(cr,uid,cr_desig_track_ids[0]).designation_id.id or False
                    if cr_designation_id:
                    #####Check weather that designation have assigned access groups
                        cr.execute('select gid from job_res_group_rel where jid = %s'%(cr_designation_id))
                        cr_access_groups_ids = map(lambda x: x[0], cr.fetchall())
                        if cr_access_groups_ids:
                            if res_users_ids:
                            #####Get access groups ids of that designation i.e. employee current designation
                                cr.execute('select gid from res_groups_users_rel where uid = %s'%(res_users_ids[0]))
                                res_groups_users_rel_ids = map(lambda x: x[0], cr.fetchall())
                            #####If employee have assigned access groups
                            #####then it's delete that access groups first and assign current designation's access groups                            
                                if len(res_groups_users_rel_ids)>0:
                                    cr.execute('delete from res_groups_users_rel where uid = %s'%(res_users_ids[0]))  
                                    if emp_active == True:
                                        for cr_access_groups_id in cr_access_groups_ids:
                                            cr.execute('insert into res_groups_users_rel (uid, gid) values(%s,%s)'%(res_users_ids[0],cr_access_groups_id))
                                            logger.info("For external employee id %s access group %s assigned"%(dealer_id, cr_access_groups_id))
                                else:
                                    if emp_active == True:
                                        for cr_access_groups_id in cr_access_groups_ids:
                                            cr.execute('insert into res_groups_users_rel (uid, gid) values(%s,%s)'%(res_users_ids[0],cr_access_groups_id))
                                            logger.info("For external employee id %s access group %s assigned"%(dealer_id, cr_access_groups_id))
                            else:
                                raise osv.except_osv(('Warning!!!'),('Employee is not active in res_users'))   
                            #####If employee does not have access groups
                            #####assign current designation's access groups                            
                        else:
                            raise osv.except_osv(('Warning!!!'),('For this job designation Access group is not assigned. Kindly assign access group first in Job Position and then try.'))   
        #####End Assign Access rights - Unlink Function
    #####Start Update res_user for jasper

    #####Define hr_tab
        if dealer_id:

            emp_no = hr_tab.browse(cr,uid,dealer_id).emp_no or False
            if emp_no:
                res_users_id = res_users_obj.search(cr,uid,[('login','=',emp_no)])
                if res_users_id:
                    res_users_obj.write(cr,uid,res_users_id,{'login':emp_no}) 
    #####End Update res_user for jasper

    #####Restrict user from making designation tracker line blank
        res = super(designation_tracker, self).unlink(cr, uid, ids, context=context)

        if not res:
            raise osv.except_osv(('Alert!!'),('Add at least one record in Designation Tracker.'))
        return res
        
designation_tracker()




################# Inherited Class of Human Resource Employees #################
class hr_employee(osv.osv):
    _inherit = "hr.employee"
    _columns = {
                    #'employee_dealer_code': fields.many2one('dealer.class', 'Dealer Class'),
                    'employee_dealerclass': fields.one2many('dealer.class', 'dealer_id','Employee Dealer Class'),
                    'desig_tracker':fields.one2many('designation.tracker', 'dealer_id', 'Designation Tracker'),
                    'employment_type': fields.many2one('hr.employee.type', 'Employment Type'),
                    'store_id':fields.many2one('sap.store', 'Home/Base Store'),
		    'birthday_text':fields.char('Date of Birth(mm/dd)'),
                    'terminate_date':fields.date('Termination Date'),
                    'base_store_id':fields.many2one('sap.store','Corporate Store'),
                    'covering_market_ids': fields.many2many('market.place', 'hr_id_market_id', 'hr_id', 'market_id', 'Covering Market',help="Markets assigned to or managed by these employees"),
                    'covering_region_ids': fields.many2many('market.regions', 'hr_id_region_id', 'hr_id', 'region_id', 'Covering Region',help="Regions assigned to or managed by these employees"),

                }

    def onchange_user(self, cr, uid, ids, user_id, context=None):
        res = super(hr_employee, self).onchange_user(cr, uid, ids, user_id, context=context)
        emp_no = False
        if user_id:
            login = self.pool.get('res.users').browse(cr, uid, user_id, context=context).sap_id.id
            res.setdefault('value', {}).update({'store_id' : login})
        return res

    def create(self, cr, uid, vals, context=None):
        birthday_text = str('')

        if vals.has_key('birthday') and vals['birthday']:
            birthday = vals['birthday']
            birthday = datetime.datetime.strptime(birthday,'%Y-%m-%d').date()
            birthday_day = birthday.day
            birthday_month = birthday.month
            birthday_text += str('%s-%s'%(birthday_month,birthday_day))
            vals.update({'birthday_text':birthday_text})
#        logger.error("**********************Create: %s"%(vals))
        res = super(hr_employee, self).create(cr, uid, vals, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        birthday_text = str('')

        if vals.has_key('birthday') and vals['birthday']:
            birthday = vals['birthday']
            birthday = datetime.datetime.strptime(birthday,'%Y-%m-%d').date()
            birthday_day = birthday.day
            birthday_month = birthday.month
            birthday_text += str('%s-%s'%(birthday_month,birthday_day))
            vals.update({'birthday_text':birthday_text})
#        logger.error("**********************Write: %s"%(vals))
        res = super(hr_employee, self).write(cr, uid, ids, vals, context=context)

        if 'terminate_date' in vals:
            terminate_date = vals['terminate_date']
        else:
            terminate_date = self.browse(cr,uid,ids).terminate_date or False

        if 'emp_no' in vals:
            emp_no = vals['emp_no']
        else:
            emp_no = self.browse(cr,uid,ids).emp_no or False


        if 'active' in vals:
            active = vals['active']
            if not active and not terminate_date:
                raise osv.except_osv(('Warning!!!'),("You can not make employee inactive without entering Termination Date. Please enter Termination Date of employee, it'll make that employee inactive automatically"))

    #####Create object of designation tracker and dealer class and
    #####Get the id of according to his/her latest end date
        desig_tracker_obj = self.pool.get('designation.tracker')
        dealer_class_obj = self.pool.get('dealer.class')
        res_users_obj = self.pool.get('res.users')
        res_users_ids = res_users_obj.search(cr,uid,[('login','=',emp_no)])
        if not res_users_ids:
            cr.execute('select id from res_users where active = False and login = %s',(emp_no,))
            res_users_ids = map(lambda x: x[0], cr.fetchall())
        dealer_class_id = []
        desig_tracker_id = []

        if terminate_date and context:
            desig_tracker_ids = desig_tracker_obj.search(cr,uid,[('dealer_id','=',ids[0])], order='end_date desc')
            dealer_class_ids = dealer_class_obj.search(cr,uid,[('dealer_id','=',ids[0])], order='end_date desc')
        #####Start validation for Termination date entered or if it's present
        #####Validation for dealer class
            if dealer_class_ids:
                dealer_class = dealer_class_ids[0]
                dealer_class_id.append(dealer_class)
            #####Check Termination Date with Employee current/latest start Date in dealer class
                dealer_class_start_date = dealer_class_obj.browse(cr,uid,dealer_class_id).start_date or False
                if dealer_class_start_date and terminate_date < dealer_class_start_date:
                    raise osv.except_osv(('Warning!!!'),('Check Date you have entered for employee. Termination date should be greater than start date of the latest record of dealer code record.'))
        #####Validation for desgnation tracker
            if desig_tracker_ids:
                desig_tracker = desig_tracker_ids[0]
                desig_tracker_id.append(desig_tracker)
            #####Check Termination Date with Employee current/latest start Date in designation tracker
                desig_start_date = desig_tracker_obj.browse(cr,uid,desig_tracker_id).start_date or False
                if desig_start_date and terminate_date < desig_start_date:
                    raise osv.except_osv(('Warning!!!'),('Check Date you have entered for employee. Termination date should be greater than start date of the latest record of designation tracker'))
                else:
                    desig_end_date = desig_tracker_obj.browse(cr,uid,desig_tracker_id).end_date or False
                    dealer_class_end_date = dealer_class_obj.browse(cr,uid,dealer_class_id).end_date or False

                    if desig_end_date and terminate_date < desig_end_date:
                        desig_tracker_obj.write(cr,uid,desig_tracker_id, {'end_date':terminate_date})
                    elif terminate_date != desig_end_date:
                        raise osv.except_osv(('Warning!!!'),('Check Date you have entered for employee. Latest End Date in Designation Tracker is less than Termination Date.'))


                    if dealer_class_ids:
                        if dealer_class_end_date and terminate_date < dealer_class_end_date:
                            dealer_class_obj.write(cr,uid,dealer_class_id, {'end_date':terminate_date,})
                        elif terminate_date != dealer_class_end_date:
                            raise osv.except_osv(('Warning!!!'),('Check Date you have entered for employee. Latest End Date in Dealer Class is less than Termination Date.'))


                #####Make employee and respective user inactive
                    self.write(cr, uid, ids,{'active':False})
                    if res_users_ids:
                        res_users_obj.write(cr,uid,res_users_ids, {'jasper_sync':False,'active':False})

        elif context:
            if res_users_ids:
                res_users_obj.write(cr,uid,res_users_ids, {'jasper_sync':True,'active':True})
            self.write(cr, uid, ids,{'active':True})

        return res


hr_employee()

class hr_job(osv.osv):
    _inherit = "hr.job"
    _columns = {
                'parent_designation': fields.many2one('hr.job','Parent Designation'),
#		'access_groups': fields.many2one('res.groups','Access Group'),
		'desig_level':fields.selection([('other','Other'), ('rsm', 'Store'), ('mm', 'Market'), ('dos', 'Region')], 'Designation Tracker Access'),
                'groups_job_rel':fields.many2many('res.groups','job_res_group_rel','jid','gid','Associated Security Group')
                # 'groups_job_rel':fields.many2many('res.groups','job_res_group_rel','jid','gid','Associated Security Group')
                }
    _defaults = {
            'desig_level':'other'
    }

    
    def write(self, cr, uid, ids, vals, context=None):
    #####Create object of employee and users  
        jasper_config_obj = self.pool.get('jasper.config')
          
        hr_employee_obj = self.pool.get('hr.employee')
        res_users_obj = self.pool.get('res.users')
        res_groups_obj = self.pool.get('res.groups')
        emp_no_list = jasper_grp_ids = []

        jasper_url = ''
        jasper_username = ''
        jasper_password = ''

        jasper_config_ids = jasper_config_obj.search(cr,uid,[])
        if not jasper_config_ids:
            raise osv.except_osv(('Warning'),("Jasper URL is not set. Check Jasper URL Configuration or else contact your admin. It's might be lost your system integration."))
        if jasper_config_ids:
            jasper_config_data = jasper_config_obj.browse(cr,uid,jasper_config_ids[0])
            jasper_url = jasper_config_data.jasper_url or False
            jasper_username = jasper_config_data.jasper_username or False
            jasper_password = jasper_config_data.jasper_password or False


    #####Check groups_job_rel field(which is in Job Position) have action or not        
        if 'groups_job_rel' in vals:
        #####Get values of groups_job_rel field from vals
            vals_groups_job_rel = vals['groups_job_rel'][0]
            
        #####Get group ids of respective job postion            
            gid = vals_groups_job_rel[2]

        #####Start Handling for jasper group ROLE_USER which is manadtory for all your
            if gid:
                jasper_grp_ids = res_groups_obj.search(cr,uid,[('id','in',gid),('jasper_check','=',True)])                   
                if jasper_grp_ids:
                    role_user_ids = res_groups_obj.search(cr,uid,[('name','=','ROLE_USER'),('group_tenantId','=',False),('jasper_check','=',True)]) or False
                    if role_user_ids and len(role_user_ids) > 1:
                        raise osv.except_osv(('Warning!!!'),('There have two groups with the name ROLE_USER. Kindly delete/inactive one of them or else contact to your Administrator'))   
                    elif role_user_ids:
                        if role_user_ids[0] not in jasper_grp_ids:
                            raise osv.except_osv(('Warning!!!'),('In Associated Security Group you have not selected group ROLE_USER. Kindly select it or else contact to your Administrator'))       
                    else:
                        raise osv.except_osv(('Warning!!!'),('In Associated Security Group you have not added group ROLE_USER. Kindly add or else contact to your Administrator'))  
        #####End Handling for jasper group ROLE_USER which is manadtory for all your             

        #####Get job id from Job Position        
            cr.execute('select gid from job_res_group_rel where jid = %s'%(ids[0]))
            job_res_group_rel_ids = map(lambda x: x[0], cr.fetchall())

            if job_res_group_rel_ids and gid:
                
            #####delete_records are ids which is currently deleted access group ids
                delete_records = list(set(job_res_group_rel_ids) - set(gid))
            #####insert records are ids which is newly assigned access group ids               
                insert_records = list(set(gid) - set(job_res_group_rel_ids))
            #####Get the employee which has this job position    
                emp_ids = hr_employee_obj.search(cr,uid,[('job_id','=',ids[0])])
                for emp_id in emp_ids:
                    emp_no_list.append(hr_employee_obj.browse(cr,uid,emp_id).emp_no)
                if emp_no_list:

                #####Check emp_ids is active or not
                #####It can be analyzed by checking employee in has in res_users table
                    user_ids = res_users_obj.search(cr,uid,[('login','in',emp_no_list)])
                    
                    if delete_records and user_ids:
                    #####Delete employee from each group
                        for delete_record in delete_records:
                            cr.execute('delete from res_groups_users_rel where gid = %s and uid in %s',(delete_record,tuple(user_ids)))

                    if insert_records and user_ids:
                    #####Insert each employee into each group
                        for insert_record in insert_records:
                            for user_id in user_ids:
                                cr.execute('select * from res_groups_users_rel where gid = %s and uid = %s'%(insert_record,user_id))
                                ext_user_id = map(lambda x: x[0], cr.fetchall())
                                if not ext_user_id:
                                    cr.execute('insert into res_groups_users_rel (gid, uid) values(%s,%s)'%(insert_record,user_id))
                #####Start Jasper Group's Sync Functionality 
                #####Don't forget to import jasper at top
                    if user_ids :
                    #####Get the ids from res_users which have jasper asctive is true 
                    #####and user is active user in odoo system.                       
                        jasper_user_ids = res_users_obj.search(cr,uid,[('jasper_sync','=',True),('id','in',user_ids)])

                        if gid:
                        #####gid are the access rights groups ids in respective job position
                            jasper_role = []
                            role_tenantId = []
                            if jasper_grp_ids:
                            #####jasper_grp_ids are the ids in gid which have jasper_check is true
                                for jasper_grp_id in jasper_grp_ids:
                                #####Fetch group name from respective jasper group
                                    group_name = res_groups_obj.browse(cr,uid,jasper_grp_id).name        
                                    group_tenantId = res_groups_obj.browse(cr,uid,jasper_grp_id).group_tenantId or ''
                                #####and append it list
                                    jasper_role.append(group_name)
                                    role_tenantId.append(group_tenantId)

                        if jasper_user_ids:
                            for jasper_user_id in jasper_user_ids:
                            #####Fetch respective data for jasper user
                                username = res_users_obj.browse(cr,uid,jasper_user_id).login
                                password = res_users_obj.browse(cr,uid,jasper_user_id).password
                                fullname = res_users_obj.browse(cr,uid,jasper_user_id).name
                                user_email = res_users_obj.browse(cr,uid,jasper_user_id).email
                                jas_sync_vals = res_users_obj.browse(cr,uid,jasper_user_id).jasper_sync                                        
                                jas_enabled = 1 if jas_sync_vals else 0   
                                jas_user = jasper.jasper_user()
                            #####If all data is accurate it'll update user in jasper    
                                if username and password and fullname and jas_enabled :
                                    jas_user.edit_user(username=username,password=password,fullname=fullname,user_email=user_email,jasper_role = jasper_role,role_tenantId = role_tenantId,enabled = jas_enabled,jasper_url = jasper_url,jasper_username = jasper_username,jasper_password =jasper_password)
                                    logger.error("UserID %s is updated into jasper server"%(jasper_user_id))
                                else:
                                    if not jasper_role and jasper_user_id:
                                        logger.error("UserID %s is not updated into jasper server as it's jasper role is not defined"%(jasper_user_id))
                                    if not jas_enabled and jasper_user_id:
                                        logger.error("UserID %s is not updated into jasper server as it's jasper enabled is False"%(jasper_user_id))
                                    if not password and jasper_user_id:
                                        logger.error("User %s is not updated into jasper server as it's password is not correctly set"%(jasper_user_id))
                                    if not fullname and jasper_user_id:
                                        logger.error("UserID %s is not updated into jasper server as it's jasper fullname is False"%(jasper_user_id))
                                    if not username and jasper_user_id:
                                        logger.error("UserID %s is not updated into jasper server as it's usename is not correctly set"%(jasper_user_id))
            #####End Jasper Group's Sync Functionality
        return super(hr_job, self).write(cr, uid, ids, vals, context=context)


hr_job()

class sap_store(osv.osv):
    _inherit = 'sap.store'
    _description = "Store"
    _columns = {
                'open_date':fields.date('Open Date'),
                'street': fields.char('Street'),
                'zip': fields.char('Zip', size=24, change_default=True),
                'city': fields.char('City'),
                'state': fields.char('State'),
                'phone':fields.char('Phone Number'),
                'fax':fields.char('Fax Number'),
                'description':fields.text('Description'),
                'website':fields.char('Website'),
                'email':fields.char('Store Email'),
                'wv_store':fields.char("WV store name"),
                'hours_operation':fields.one2many('store.hours.operation','store_id','Hours of Operation'),
                'sap_tracker':fields.one2many('sap.tracker', 'sap_id', 'SAP Tracker'),
                'active':fields.boolean('Active'),
                'ip_add':fields.char('IP Address'),
    }
    _defaults = {
                'active':True
    }
    _sql_constraints = [
                ('sap_number_uniq', 'unique(sap_number)', 'SAP # must be unique!'),
    ]

    def write(self, cr, uid, ids, vals, context=None):
        hr_obj = self.pool.get('hr.employee')
        sap_track_obj = self.pool.get('sap.tracker')
        sap_track_ids = sap_track_obj.search(cr,uid,[('sap_id','=',ids)],order = 'end_date desc')
        if sap_track_ids:
            store_inactive_vals = sap_track_obj.browse(cr,uid,sap_track_ids[0]).store_inactive or False
            if store_inactive_vals:
                store_active = False
            else:
                store_active = True
            vals.update({'active':store_active})
        res = super(sap_store, self).write(cr, uid, ids, vals, context=context)
        if 'active' in vals:
            active_vals = vals['active']
        else:
            active_vals = self.browse(cr, uid, ids).active or False
        if not active_vals:
            if isinstance(ids,(list)):
                ids = ids[0]
            hr_emp_ids = hr_obj.search(cr,uid,[('store_id','=',ids)])
            if hr_emp_ids and len(hr_emp_ids)>0:
                emp_length = len(hr_emp_ids)
                raise osv.except_osv(('Warning!!!'),('%s Employees are exist on this store.\nBefore inactive the store, transfer all employee of this particular store into other store.'%(emp_length)))
        return res

#    _rec_name = 'name'

sap_store()

_week_day = [('mon','Monday'),('tue','Tuesday'),('wed','Wednesday'),('thurs','Thursday'),('fri','Friday'),('sat','Saturday'),('sun','Sunday')]

class store_hours_operation(osv.osv):
    _name = 'store.hours.operation'
    _columns = {
                'store_id':fields.many2one('sap.store','Store Id'),
                'from_day':fields.selection(_week_day,'From Day'),
                'upto_day':fields.selection(_week_day,'Upto Day'),
                'start_time':fields.char('Opening Time'),
                'end_time':fields.char('Closing Time')
    }
store_hours_operation()

class market_place(osv.osv):
    _inherit = 'market.place'
    _description = "Market"
    _columns = {
        'market_tracker':fields.one2many('market.tracker', 'market_id', 'Market Tracker'),
    }    

    def create(self, cr, uid, vals, context=None):
        hr_obj = self.pool.get('hr.employee')
        user_obj = self.pool.get('res.users')
        res = super(market_place, self).create(cr, uid, vals, context=context)
        hr_id = vals['market_manager']
        region_id = vals['region_market_id']
        hr_data = hr_obj.browse(cr, uid, hr_id)
        user_id = hr_data.user_id.id
        user_obj.write(cr, SUPERUSER_ID, [user_id], {'market_id':res,'region_id':region_id})
        return res

    def write(self, cr, uid, ids, vals, context=None):
        # *********************************************************************************** #
        ###################### Sync with Users Master (method 1) for access rights ####################
        hr_obj = self.pool.get('hr.employee')
        user_obj = self.pool.get('res.users')
        hr_id = False
        region_id = False
        if 'market_manager' in vals:
            hr_id = vals['market_manager']
        if 'region_market_id' in vals:
            region_id = vals['region_market_id']
        if not hr_id:
            hr_id = self.browse(cr, uid, ids[0]).market_manager.id
        if not region_id:
            region_id = self.browse(cr, uid, ids[0]).region_market_id.id
        if hr_id:
            hr_data = hr_obj.browse(cr, uid, hr_id)
            user_id = hr_data.user_id.id
            user_obj.write(cr, SUPERUSER_ID, [user_id], {'market_id':ids[0],'region_id':region_id})
        res = super(market_place, self).write(cr, uid, ids, vals, context=context)
        return res

market_place()

class market_regions(osv.osv):
    _inherit = 'market.regions'
    _description = "Region"
    _columns = {
        'region_tracker':fields.one2many('region.tracker', 'region_id', 'Region Tracker'),
    }    

    def create(self, cr, uid, vals, context=None):
        hr_obj = self.pool.get('hr.employee')
        user_obj = self.pool.get('res.users')
        res = super(market_regions, self).create(cr, uid, vals, context=context)
        hr_id = vals['sales_director']
        hr_data = hr_obj.browse(cr, uid, hr_id)
        user_id = hr_data.user_id.id
        user_obj.write(cr, SUPERUSER_ID, [user_id], {'region_id':res})
        return res

    def write(self, cr, uid, ids, vals, context=None):
        hr_obj = self.pool.get('hr.employee')
        user_obj = self.pool.get('res.users')
        if ('sales_director' in vals) and vals['sales_director']:
            hr_id = vals['sales_director']
            hr_data = hr_obj.browse(cr, uid, hr_id)
            user_id = hr_data.user_id.id
            user_obj.write(cr, SUPERUSER_ID, [user_id], {'region_id':ids[0]})
        res = super(market_regions, self).write(cr, uid, ids, vals, context=context)
        return res

market_regions()

class res_users(osv.osv):
    _inherit = 'res.users'
    _columns = {
                'market_id':fields.many2one('market.place', 'Market'),
                'region_id':fields.many2one('market.regions', 'Region'),
    }

    def onchange_sap(self, cr, uid, ids, sap_id):
        sap_obj = self.pool.get('sap.store')
        if sap_id:
            sap_data = sap_obj.browse(cr, uid, sap_id)
            market_id = sap_data.market_id.id
            region_id = sap_data.market_id.region_market_id.id
            return {'value':{'market_id':market_id,'region_id':region_id}}
        return {'value':{'market_id':False,'region_id':False}}

# *************** Due to Odoo 8 users import issue *********************** ###

    def create(self, cr, uid, vals, context=None):
############ Context pass to dealer class for skipping updation of store in user master while creating user #####
        context.update({'user_create':True})
######### ends here ##########
        partner_obj = self.pool.get('res.partner')
	sap_obj = self.pool.get('sap.store')
        #### to update the vals with sap store market and region
        if vals.has_key('sap_id') and vals['sap_id']:
            sap_cur_obj = sap_obj.browse(cr, uid, vals['sap_id'])
            vals.update({'market_id': sap_cur_obj.market_id.id,'region_id': sap_cur_obj.market_id.region_market_id.id})

        ######### code ends here ####################

        logger.info("vvvvvvvvvvvvvvvvvvvvvvvvvv %s"%(vals))
        if not vals.has_key('partner_id') or (vals.has_key('partner_id') and not vals['partner_id']):
           # logger.info("vvvvvvvvvvvvvvvvvvvvvvvvvv %s"%(vals['partner_id']))
            partner_id = partner_obj.create(cr, uid, {'name': vals['name']})
            vals.update({'partner_id': partner_id,'email' : vals['email']})
        user_id = super(res_users, self).create(cr, uid, vals, context=context)
        user = self.browse(cr, uid, user_id, context=context)
        if user.partner_id.company_id:
            user.partner_id.write({'company_id': user.company_id.id})
        return user_id

res_users()

class change_password_wizard(osv.TransientModel):
    _name = 'change.password.wizard'
    _inherit = "change.password.wizard"

change_password_wizard()

class stores_classification(osv.osv):
    _inherit = 'stores.classification'
    _columns = {
                'cal_level':fields.many2one('ir.model','Calculation Level')

    }
stores_classification()

################Code by pratik

class sap_tracker(osv.osv):
    _name = 'sap.tracker'
    _description = "SAP Tracker"
    _columns = {
                'start_date':fields.date('Start Date'),
                'end_date':fields.date('End Date'),
                'sap_id':fields.many2one('sap.store', 'Store Id'),
                'market_id' : fields.many2one('market.place','Market', required="1"),
                'store_mgr_id' : fields.many2one('hr.employee','Store Manager'),
                'desig_id':fields.many2one('designation.tracker', 'Designation Tracker'),
                'store_inactive':fields.boolean('Inactive'),
                'store_comments':fields.char('Comments'),
                'designation_id':fields.many2one('hr.job', 'Job Position'),
    }

    def create(self, cr, uid, vals, context=None):
        res = super(sap_tracker, self).create(cr, uid, vals, context=context)
        hr_obj = self.pool.get('hr.employee')
        user_obj = self.pool.get('res.users')
        hr_job_obj = self.pool.get('hr.job')
        designation_tracker_obj = self.pool.get('designation.tracker')
        sap_store_obj =  self.pool.get('sap.store')        
        values = {}
        store_mgr_id =  vals.get('store_mgr_id', False)
        end_date =  vals.get('end_date', False)
        start_date =  vals.get('start_date', False)
        sap_id =  vals.get('sap_id', False)
        store_inactive = vals.get('store_inactive', False)
        store_comments = vals.get('store_comments', False)
        desig_id = vals.get('desig_id', False)
        designation_id = vals.get('designation_id',False)


        values.update({'heirarchy_level': 'rsm', 'covering_str_check': False, 
            'covering_market_check':False,'covering_region_check':False,
            'market_id':False,'region_id':False})


        if 'store_mgr_id' in vals:
            values.update({'dealer_id': vals.get('store_mgr_id' )})
        if 'end_date' in vals:
            values.update({'end_date': vals.get('end_date' )})
        if 'start_date' in vals:
            values.update({'start_date': vals.get('start_date' )})
        if 'sap_id' in vals:
            values.update({'store_name': vals.get('sap_id' )})

        if not 'store_inactive' in vals:
            vals.update({'store_inactive':False})
        if not 'store_comments' in vals:
            vals.update({'store_comments':False})
        if 'market_id' in vals:
            market_id = vals.get('sap_id', False)

        if 'store_inactive' in vals:
            vals.update({'store_inactive':store_inactive})
        if 'store_comments' in vals:
            vals.update({'store_comments':store_comments})

        if 'designation_id' in vals:
            values.update({'designation_id': vals.get('designation_id',False)})

    #####Handling
        if isinstance(end_date, (str)):
            check_end_date = (datetime.datetime.strptime(end_date, '%Y-%m-%d'))
        else:
            check_end_date = end_date

        if isinstance(start_date, (str)):
            check_start_date = (datetime.datetime.strptime(start_date, '%Y-%m-%d'))
        else:
            check_start_date = start_date    
    #####Start date is greater than end date
        if context and (check_start_date and check_end_date):
            if check_start_date > check_end_date:
                raise osv.except_osv(('Warning!!!'),('End date should be greater than start date. Check dates you have entered.'))

        #####Not allow user to enter designation for same period 
            if sap_id and start_date and end_date:
                sap_tracker_ids = self.search(cr, uid, [('sap_id','=',sap_id),('start_date','<=',start_date),('end_date','>=',end_date)])
                if sap_tracker_ids and len(sap_tracker_ids) > 1:
                    raise osv.except_osv(('Warning!!'),('Period for which you are updating designation already exist.\nCheck the dates you have entered.'))

                sap_tracker_ids = self.search(cr, uid, [('sap_id','=',sap_id),('end_date','>=',start_date), ('start_date','<',end_date)])
                if sap_tracker_ids and len(sap_tracker_ids) > 1:
                    raise osv.except_osv(('Warning!!'),('Previous designation exist on this start date.\nCheck the dates you have entered.'))

        #####Start date is greater than end date
        if context:
      
            if not store_inactive and store_mgr_id and values and context:
                desig_id = designation_tracker_obj.create(cr, uid, values, context=context)
                if desig_id:
                    self.write(cr,uid,res,{'desig_id':desig_id})
                    track_ids = self.search(cr,uid,[('desig_id','=',desig_id),('id','=',res)])
                    if not track_ids:
                        cr.execute("update sap_tracker set desig_id=%s where id=%s "%(desig_id,res))
        #####Sap tracker id takes a latest sap_tracker id
            if sap_id:
                sap_track_ids = self.search(cr, uid, [('sap_id','=',sap_id)],order = 'end_date desc')
                if sap_track_ids:
                    ext_market_id = self.browse(cr,uid,sap_track_ids[0]).market_id.id or False
                    ext_store_mgr_id = self.browse(cr,uid,sap_track_ids[0]).store_mgr_id.id or False
                    if ext_market_id:
                        sap_store_obj.write(cr,uid,sap_id,{'market_id':ext_market_id})      
                    if ext_store_mgr_id:
                        sap_store_obj.write(cr,uid,sap_id,{'store_mgr_id':ext_store_mgr_id})
                    else:
                        sap_store_obj.write(cr,uid,sap_id,{'store_mgr_id':False})

        #####Commented on 09/07/2015
            # if store_inactive:
            #     sap_store_obj.write(cr,uid,sap_id,{'active':False})
            # else:
            #     sap_store_obj.write(cr,uid,sap_id,{'active':True})

        if desig_id and sap_id:
            dup_sap_track_ids = self.search(cr, uid, [('sap_id','=',sap_id),('desig_id','=',desig_id)],order = 'id desc')
            if dup_sap_track_ids and len(dup_sap_track_ids)>1:
                self.unlink(cr,uid,dup_sap_track_ids[0])
        return res  

    def write(self, cr, uid, ids, vals, context=None):
        hr_obj = self.pool.get('hr.employee')
        user_obj = self.pool.get('res.users')
        hr_job_obj = self.pool.get('hr.job')
        designation_tracker_obj = self.pool.get('designation.tracker')
        sap_store_obj = self.pool.get('sap.store')
        hr_obj = self.pool.get('hr.employee')
        sap_store_obj = self.pool.get('sap.store')
        hr_obj = self.pool.get('hr.employee')
        self_data = self.browse(cr,uid,ids)
        sap_params = store_name = sap_store_id = False


        
        if 'start_date' in vals:
            start_date = vals['start_date']
        else:
            start_date = self_data.start_date or False
        
        if 'end_date' in vals:
            end_date = vals['end_date']
            ext_end_date = self_data.end_date or False
        else:
            end_date = self_data.end_date or False

        if 'desig_id' in vals:
            desig_id = vals['desig_id']
        else:
            desig_id = self_data.desig_id.id or False

        if 'store_mgr_id' in vals:
            store_mgr_id = vals['store_mgr_id']
        else:
            store_mgr_id = self_data.store_mgr_id.id or False  

        if 'sap_id' in vals:
            sap_id = vals.get('sap_id')
        else:
            sap_id = self_data.sap_id.id or False    
            
        if 'market_id' in vals:
            market_id = vals['market_id']    
        else:
            market_id = self_data.market_id.id or False  

        if 'store_inactive' in vals:
            store_inactive = vals['store_inactive']    
        else:
            store_inactive = self_data.store_inactive or False 

        if 'store_comments' in vals:
            store_comments = vals['store_comments']    
        else:
            store_comments = self_data.store_comments or False 


        if 'designation_id' in vals:
            designation_id = vals.get('designation_id',False)
        else:
            designation_id = self_data.designation_id.id or False   

        values = {}
        if store_mgr_id:
            values.update({'dealer_id': store_mgr_id})
        if end_date:
            values.update({'end_date': end_date})
        if start_date:
            values.update({'start_date': start_date})
        if sap_id:
            values.update({'store_name': sap_id})
        if designation_id:
            values.update({'designation_id':designation_id})



        values.update({'heirarchy_level': 'rsm', 'covering_str_check': False, 
            'covering_market_check':False,'covering_region_check':False,
            'market_id':False,'region_id':False})

        if isinstance(end_date, (str)):
            check_end_date = (datetime.datetime.strptime(end_date, '%Y-%m-%d'))
        else:
            check_end_date = end_date

        if isinstance(start_date, (str)):
            check_start_date = (datetime.datetime.strptime(start_date, '%Y-%m-%d'))
        else:
            check_start_date = start_date    
    #####Start date is greater than end date

        res = super(sap_tracker, self).write(cr, uid, ids, vals, context=context)  

        if context:
            if (check_start_date and check_end_date) and (check_start_date > check_end_date):
                raise osv.except_osv(('Warning!!!'),('End date should be greater than start date. Check dates you have entered.'))
        #####Not allow user to enter designation for same period 
            sap_tracker_ids = self.search(cr, uid, [('sap_id','=',sap_id),('start_date','<=',check_start_date),('end_date','>=',check_end_date)])
            if sap_tracker_ids and len(sap_tracker_ids) > 1:
                raise osv.except_osv(('Warning!!'),('Period for which you are updating designation already exist.\nCheck the dates you have entered.'))

            sap_tracker_ids = self.search(cr, uid, [('sap_id','=',sap_id),('end_date','>=',check_start_date), ('start_date','<=',check_end_date)])
            if sap_tracker_ids and len(sap_tracker_ids) > 1:
                raise osv.except_osv(('Warning!!'),('Previous designation exist on this start date.\nCheck the dates you have entered.'))

            if 'params' in context:
                context_params = context.get('params')
                if context_params and 'model' in context_params:
                    params_model = context_params.get('model')  
                    if params_model and params_model in ('sap.store') and 'id' in context_params:
                        sap_store_id = context_params.get('id')  

        #####Start create user in designation tracker - Write Function
            if not store_inactive and store_mgr_id and values and context:
                desig_id = designation_tracker_obj.create(cr, uid, values, context=context)
                if desig_id:
                    self.write(cr,uid,ids,{'desig_id':desig_id})
                    track_ids = self.search(cr,uid,[('desig_id','=',desig_id),('id','=',ids)])
                    if not track_ids:
                        cr.execute("update sap_tracker set desig_id=%s where id=%s "%(desig_id,res))
        #####Sap tracker id takes a latest sap_tracker id
            if sap_id:
                sap_track_ids = self.search(cr, uid, [('sap_id','=',sap_id)],order = 'end_date desc')
                if sap_track_ids:
                    ext_market_id = self.browse(cr,uid,sap_track_ids[0]).market_id.id or False
                    ext_store_mgr_id = self.browse(cr,uid,sap_track_ids[0]).store_mgr_id.id or False
                    if ext_market_id:
                        sap_store_obj.write(cr,uid,sap_id,{'market_id':ext_market_id})      
                    if ext_store_mgr_id:
                        sap_store_obj.write(cr,uid,sap_id,{'store_mgr_id':ext_store_mgr_id})
                    else:
                        sap_store_obj.write(cr,uid,sap_id,{'store_mgr_id':False})

        #####Commented on 09/07/2015
            # if store_inactive:
            #     sap_store_obj.write(cr,uid,sap_id,{'active':False})
            # else:
            #     sap_store_obj.write(cr,uid,sap_id,{'active':True})
        #####End create user in designation tracker - Write Function
            if sap_id:
                sap_track_ids = self.search(cr, uid, [('sap_id','=',sap_id)],order = 'end_date desc')
            if sap_track_ids:
                ext_market_id = self.browse(cr,uid,sap_track_ids[0]).market_id.id
                ext_store_mgr_id = self.browse(cr,uid,sap_track_ids[0]).store_mgr_id.id
                ext_store_inactive = self.browse(cr,uid,sap_track_ids[0]).store_inactive
            if ext_market_id:
                sap_store_obj.write(cr,uid,sap_id,{'market_id':ext_market_id})
            if ext_store_mgr_id:
                sap_store_obj.write(cr,uid,sap_id,{'store_mgr_id':ext_store_mgr_id})
            else:
                sap_store_obj.write(cr,uid,sap_id,{'store_mgr_id':False})
        else:
            ext_sap_store = sap_store_obj.search(cr,uid,[('store_mgr_id','=',store_mgr_id),('id','=',sap_id)])
            if ext_sap_store and 'end_date' in vals:
                if ext_end_date and isinstance(ext_end_date, (str)):
                    ext_end_date = (datetime.datetime.strptime(ext_end_date, '%Y-%m-%d'))
                else:
                    ext_end_date = ext_end_date

                if isinstance(start_date, (str)):
                    ext_start_date = (datetime.datetime.strptime(start_date, '%Y-%m-%d')) + timedelta(days=1)
                else:
                    ext_start_date = end_date

                cr.execute('select id, end_date from sap_tracker where sap_id = %s order by end_date desc;',(sap_id,))
                latest_sap_tracker_ids = map(lambda x: x[0], cr.fetchall())

                if latest_sap_tracker_ids:
                    latest_end_date = self.browse(cr,uid,latest_sap_tracker_ids[0]).end_date or False
                    if latest_end_date and isinstance(latest_end_date, (str)):
                        latest_end_date = (datetime.datetime.strptime(latest_end_date, '%Y-%m-%d'))
                    if (latest_end_date and ext_end_date) and (latest_end_date < ext_end_date):
                        values = {
                        'start_date' :  check_end_date + datetime.timedelta(days=1),
                        'end_date' : check_end_date + datetime.timedelta(days=2192),####2190 days = 6 years                        
                        'market_id' : market_id,
                        'sap_id':sap_id,
                        }
                        self.create(cr,uid,values,context)
        if desig_id and sap_id:
            dup_sap_track_ids = self.search(cr, uid, [('sap_id','=',sap_id),('desig_id','=',desig_id)],order = 'id desc')
        else:
            dup_sap_track_ids = []
        if dup_sap_track_ids and len(dup_sap_track_ids)>1:
            self.unlink(cr,uid,dup_sap_track_ids[0])
        if sap_id:
            sap_track_ids = self.search(cr, uid, [('sap_id','=',sap_id)],order = 'end_date desc')
            if sap_track_ids:
                ext_market_id = self.browse(cr,uid,sap_track_ids[0]).market_id.id or False
                ext_store_mgr_id = self.browse(cr,uid,sap_track_ids[0]).store_mgr_id.id or False
                if ext_market_id:
                    sap_store_obj.write(cr,uid,sap_id,{'market_id':ext_market_id})
                if ext_store_mgr_id:
                    sap_store_obj.write(cr,uid,sap_id,{'store_mgr_id':ext_store_mgr_id})
                else:
                    sap_store_obj.write(cr,uid,sap_id,{'store_mgr_id':False})

        return res

sap_tracker()



class market_tracker(osv.osv):
    _name = 'market.tracker'
    _description = "Market Tracker"
    _columns = {
                'start_date':fields.date('Start Date'),
                'end_date':fields.date('End Date'),
                'region_market_id':fields.many2one('market.regions','Region'),
                'market_manager': fields.many2one('hr.employee','Market Manager'),
                'market_id':fields.many2one('market.place', 'Market Id'),
                'track_market_id':fields.many2one('market.place', 'Market Id'),
                'desig_id':fields.many2one('designation.tracker', 'Designation Tracker'),
                'designation_id':fields.many2one('hr.job', 'Job Position'),                
    }


    def create(self, cr, uid, vals, context=None):
        logger.error("Market Vals : %s"%(vals)) 
        hr_obj = self.pool.get('hr.employee')
        user_obj = self.pool.get('res.users')
        hr_job_obj = self.pool.get('hr.job')
        market_place_obj = self.pool.get('market.place')
        designation_tracker_obj = self.pool.get('designation.tracker')
        values = {}
        res = []
        if 'market_manager' in vals:
            market_manager = vals.get('market_manager', False)
            values.update({'dealer_id': vals.get('market_manager', False)})
        if 'start_date' in vals:
            start_date = vals.get('start_date', False)
            values.update({'start_date': vals.get('start_date', False)})
        if 'end_date' in vals:
            end_date = vals.get('end_date', False)
            values.update({'end_date': vals.get('end_date', False)})
        if 'desig_id' in vals:
            desig_id = vals.get('desig_id', False)
        else:
            desig_id = False

        if 'market_id' in vals:
            market_id = vals.get('market_id', False)
            values.update({'market_id': vals.get('market_id', False)})
        if 'region_market_id' in vals:
            region_market_id = vals.get('region_market_id', False)

        if 'designation_id' in vals:
            designation_id = vals.get('designation_id',False)
            values.update({'designation_id': vals.get('designation_id',False)})

        values.update({'heirarchy_level': 'mm', 'covering_str_check': False, 
            'covering_market_check':False,'covering_region_check':False,
            'store_name':False,'region_id':False})

        # hr_job_ids = hr_job_obj.search(cr, uid, [('desig_level','=','mm'),('model_id','=','mm')])
        # if hr_job_ids and len(hr_job_ids) > 1:
        #     raise osv.except_osv(_('Error !'),_("Please check job position. There have two records which have Heirarchy Level is MM and  Designation Tracker Access is Market. Kindly change it or contact to Administrator"))
        # elif hr_job_ids:
        #     values.update({'designation_id': hr_job_ids[0]})
        #     values.update({'heirarchy_level': 'MM'})
        #     values.update({'covering_str_check': False, 'covering_market_check':False,'covering_region_check':False,'store_name':False,'region_id':False})            

        if isinstance(end_date, (str)):
            check_end_date = (datetime.datetime.strptime(end_date, '%Y-%m-%d'))
        else:
            check_end_date = end_date

        if isinstance(start_date, (str)):
            check_start_date = (datetime.datetime.strptime(start_date, '%Y-%m-%d'))
        else:
            check_start_date = start_date    
    #####Start date is greater than end date
        if context and  check_start_date and check_end_date:
            if check_start_date > check_end_date:
                raise osv.except_osv(('Warning!!!'),('End date should be greater than start date. Check dates you have entered.'))

        #####Not allow user to enter designation for same period 
            market_tracker_ids = self.search(cr, uid, [('market_id','=',market_id),('start_date','<=',check_start_date),('end_date','>=',check_end_date)])
            if market_tracker_ids and len(market_tracker_ids) > 1:
                raise osv.except_osv(('Warning!!'),('Period for which you are updating designation already exist.\nCheck the dates you have entered.'))

            market_tracker_ids = self.search(cr, uid, [('market_id','=',market_id),('end_date','>=',check_start_date), ('start_date','<',check_end_date)])
            if market_tracker_ids and len(market_tracker_ids) > 1:
                raise osv.except_osv(('Warning!!'),('Previous designation exist on this start date.\nCheck the dates you have entered.'))
        res = super(market_tracker, self).create(cr, uid, vals, context=context)
    #####Start Handling for start date and end date
        if context and market_manager:
            desig_id = designation_tracker_obj.create(cr, uid, values, context=context)
            if desig_id:
                self.write(cr,uid,res,{'desig_id':desig_id})
                track_ids = self.search(cr,uid,[('desig_id','=',desig_id),('id','=',res)])
                if not track_ids:
                    cr.execute("update market_tracker set desig_id=%s where id=%s "%(desig_id,res))
        if market_id:
            market_track_ids = self.search(cr, uid, [('market_id','=',market_id)],order = 'end_date desc')
            if market_track_ids:
                ext_market_region_id = self.browse(cr,uid,market_track_ids[0]).region_market_id.id
                ext_market_mgr_id = self.browse(cr,uid,market_track_ids[0]).market_manager.id
                if ext_market_region_id:
                    market_place_obj.write(cr,uid,[market_id],{'region_market_id':ext_market_region_id})
                if ext_market_mgr_id:
                    market_place_obj.write(cr,uid,[market_id],{'market_manager':ext_market_mgr_id})
                else:
                    market_place_obj.write(cr,uid,[market_id],{'market_manager':False})
        return res      

    def write(self, cr, uid, ids, vals, context=None):
        hr_obj = self.pool.get('hr.employee')
        user_obj = self.pool.get('res.users')
        hr_job_obj = self.pool.get('hr.job')
        market_place_obj = self.pool.get('market.place')
        designation_tracker_obj = self.pool.get('designation.tracker')
        self_data = self.browse(cr,uid,ids)
        values = {}

        if 'market_manager' in vals:
            market_manager = vals.get('market_manager')
        else:
            market_manager = self_data.market_manager.id or False

        if 'start_date' in vals:
            start_date = vals.get('start_date')
        else:
            start_date = self_data.start_date or False

        if 'end_date' in vals:
            end_date = vals.get('end_date')
            ext_end_date = self_data.end_date or False           
        else:
            end_date = self_data.end_date or False

        if 'desig_id' in vals:
            desig_id = vals.get('desig_id')
        else:
            desig_id = self_data.desig_id.id or False

        if 'market_id' in vals:
            market_id = vals.get('market_id')
        else:
            market_id = self_data.market_id.id or False

        if 'region_market_id' in vals:
            region_market_id = vals.get('region_market_id')
        else:
            region_market_id = self_data.region_market_id.id or False

        if 'designation_id' in vals:
            designation_id = vals.get('designation_id',False)
        else:
            designation_id = self_data.designation_id.id or False

        if market_manager:   
            values.update({'dealer_id': market_manager})
        if start_date:
            values.update({'start_date': start_date})
        if end_date:
            values.update({'end_date': end_date})
        if market_id:
            values.update({'market_id': market_id})
        if designation_id:
            values.update({'designation_id': designation_id})


        values.update({'heirarchy_level': 'mm', 'covering_str_check': False, 
            'covering_market_check':False,'covering_region_check':False,
            'store_name':False,'region_id':False})

        if isinstance(end_date, (str)):
            check_end_date = (datetime.datetime.strptime(end_date, '%Y-%m-%d'))
        else:
            check_end_date = end_date

        if isinstance(start_date, (str)):
            check_start_date = (datetime.datetime.strptime(start_date, '%Y-%m-%d'))
        else:
            check_start_date = start_date    
    #####Start date is greater than end date
        if context and check_start_date and check_end_date:
            if check_start_date > check_end_date:
                raise osv.except_osv(('Warning!!!'),('End date should be greater than start date. Check dates you have entered.'))

    #####Not allow user to enter designation for same period 
            market_tracker_ids = self.search(cr, uid, [('market_id','=',market_id),('start_date','<=',check_start_date),('end_date','>=',check_end_date)])
            if market_tracker_ids and len(market_tracker_ids) > 1:
                raise osv.except_osv(('Warning!!'),('Period for which you are updating designation already exist.\nCheck the dates you have entered.'))

            market_tracker_ids = self.search(cr, uid, [('market_id','=',market_id),('end_date','>=',check_start_date), ('start_date','<=',check_end_date)])
            if market_tracker_ids and len(market_tracker_ids) > 1:
                raise osv.except_osv(('Warning!!'),('Previous designation exist on this start date.\nCheck the dates you have entered.'))

        # hr_job_ids = hr_job_obj.search(cr, uid, [('desig_level','=','mm'),('model_id','=','mm')])
        # if hr_job_ids and len(hr_job_ids) > 1:
        #     raise osv.except_osv(_('Error !'),_("Please check job position. There have two records which have Heirarchy Level is MM and  Designation Tracker Access is Market. Kindly change it or contact to Administrator"))
        # elif hr_job_ids:
        #     values.update({'designation_id': hr_job_ids[0]})
        #     values.update({'heirarchy_level': 'MM'})
        #     values.update({'covering_str_check': False, 'covering_market_check':False,'covering_region_check':False,'store_name':False,'region_id':False})            

        res = super(market_tracker, self).write(cr, uid, ids, vals, context=context)
        # res = super(market_tracker, self).write(cr, uid, ids, vals, context=context)
            
        #####Start Handling for start date and end date
        if context:

            if market_manager:
                desig_id = designation_tracker_obj.create(cr, uid, values, context=context)
                if desig_id:
#                    self.write(cr,uid,ids,{'desig_id':desig_id})
#                    track_ids = self.search(cr,uid,[('desig_id','=',desig_id),('id','=',ids[0])])
#                    if not track_ids:
                    cr.execute("update market_tracker set desig_id=%s where id=%s "%(desig_id,ids[0]))
						
            if market_id and region_market_id:
                market_place_obj.write(cr,uid,[market_id],{'region_market_id':region_market_id})

            #####Sap tracker id takes a latest sap_tracker id
            if market_id:
                market_track_ids = self.search(cr, uid, [('market_id','=',market_id)],order = 'end_date desc')
                if market_track_ids:
                    ext_market_mgr_id = self.browse(cr,uid,market_track_ids[0]).market_manager.id
                    ext_market_region_id = self.browse(cr,uid,market_track_ids[0]).region_market_id.id
                    if ext_market_region_id:
                        market_place_obj.write(cr,uid,[market_id],{'region_market_id':ext_market_region_id})
                    if ext_market_mgr_id:
                        market_place_obj.write(cr,uid,[market_id],{'market_manager':ext_market_mgr_id})
                    else:
                        market_place_obj.write(cr,uid,[market_id],{'market_manager':False})
        else:
            ext_market_ids = market_place_obj.search(cr,uid,[('market_manager','=',market_manager),('id','=',market_id)])
            if ext_market_ids and 'end_date' in vals:
                if ext_end_date and isinstance(ext_end_date, (str)):
                    ext_end_date = (datetime.datetime.strptime(ext_end_date, '%Y-%m-%d'))
                else:
                    ext_end_date = ext_end_date

                if isinstance(start_date, (str)):
                    ext_start_date = (datetime.datetime.strptime(start_date, '%Y-%m-%d'))
                else:
                    ext_start_date = end_date

                latest_market_tracker_ids = self.search(cr, uid, [('market_id','=',market_id)], order='end_date desc')

                if latest_market_tracker_ids:
                    latest_end_date = self.browse(cr,uid,latest_market_tracker_ids[0]).end_date
                    if latest_end_date and isinstance(latest_end_date, (str)):
                        latest_end_date = (datetime.datetime.strptime(latest_end_date, '%Y-%m-%d'))

                    if (latest_end_date and ext_end_date) and (latest_end_date < ext_end_date):
                        values = {
                        'start_date' :  check_end_date + datetime.timedelta(days=01),
                        'end_date' : check_end_date + datetime.timedelta(days=2192),####2190 days = 6 years
                        
                        'region_market_id' : region_market_id,
                        'market_id':market_id,
                        }
                        self.create(cr,uid,values,context)  

        if market_id and desig_id:
            dup_market_track_ids = self.search(cr, uid, [('market_id','=',market_id),('desig_id','=',desig_id)],order = 'id desc')
            if dup_market_track_ids and len(dup_market_track_ids)>1:
                self.unlink(cr,uid,dup_market_track_ids[0])

        if market_id:
            market_track_ids = self.search(cr, uid, [('market_id','=',market_id)],order = 'end_date desc')
            if market_track_ids:
                ext_market_region_id = self.browse(cr,uid,market_track_ids[0]).region_market_id.id
                ext_market_mgr_id = self.browse(cr,uid,market_track_ids[0]).market_manager.id
                if ext_market_region_id:
                    market_place_obj.write(cr,uid,[market_id],{'region_market_id':ext_market_region_id})
                if ext_market_mgr_id:
                    market_place_obj.write(cr,uid,[market_id],{'market_manager':ext_market_mgr_id})
                else:
                    market_place_obj.write(cr,uid,[market_id],{'market_manager':False})
        return res

market_tracker()

       
class region_tracker(osv.osv):
    _name = 'region.tracker'
    _description = "Region Tracker"
    _columns = {
                'start_date':fields.date('Start Date'),
                'end_date':fields.date('End Date'),
                'sales_director': fields.many2one('hr.employee', 'Director Of Sales'),
                'company_id': fields.many2one('res.company', 'Company'),
                'region_id':fields.many2one('market.regions', 'Region'),
                'track_region_id':fields.many2one('market.regions', 'Region Id'),
                'desig_id':fields.many2one('designation.tracker', 'Designation Tracker'),
                'designation_id':fields.many2one('hr.job', 'Job Position'),                
    }

    def create(self, cr, uid, vals, context=None):
        hr_obj = self.pool.get('hr.employee')
        user_obj = self.pool.get('res.users')
        hr_job_obj = self.pool.get('hr.job')
        market_region_obj = self.pool.get('market.regions')
        designation_tracker_obj = self.pool.get('designation.tracker')
        values = {}
# valsss {'region_id': 33, 'end_date': '2015-04-30', 'desig_id': False, 'company_id': 1, 
# 'sales_director': 1751, 'start_date': '2015-04-01'}

        if 'sales_director' in vals:
            sales_director = vals.get('sales_director')
            values.update({'dealer_id': vals.get('sales_director', False)})
        if 'start_date' in vals:
            start_date = vals.get('start_date')
            values.update({'start_date': vals.get('start_date', False)})
        if 'end_date' in vals:
            end_date = vals.get('end_date')
            values.update({'end_date': vals.get('end_date', False)})
        if 'desig_id' in vals:
            desig_id = vals.get('desig_id')
        else:
            desig_id = False
        if 'region_id' in vals:
            region_id = vals.get('region_id')
            values.update({'region_id': vals.get('region_id', False)})
        if 'company_id' in vals:
            company_id = vals.get('company_id', False)


        if 'designation_id' in vals:
            designation_id = vals.get('designation_id',False)
            values.update({'designation_id': vals.get('designation_id',False)})

        values.update({'heirarchy_level': 'dos', 'covering_str_check': False, 
            'covering_market_check':False,'covering_region_check':False,
            'store_name':False,'market_id':False})

        if isinstance(end_date, (str)):
            check_end_date = (datetime.datetime.strptime(end_date, '%Y-%m-%d'))
        else:
            check_end_date = end_date

        if isinstance(start_date, (str)):
            check_start_date = (datetime.datetime.strptime(start_date, '%Y-%m-%d'))
        else:
            check_start_date = start_date    
    #####Start date is greater than end date
        if context and check_start_date and check_end_date:
            if check_start_date > check_end_date:
                raise osv.except_osv(('Warning!!!'),('End date should be greater than start date. Check dates you have entered.'))

    #####Not allow user to enter designation for same period 
            region_tracker_ids = self.search(cr, uid, [('region_id','=',region_id),('start_date','<=',check_start_date),('end_date','>=',check_end_date)])
            if region_tracker_ids and len(region_tracker_ids) > 1:
                raise osv.except_osv(('Warning!!'),('Period for which you are updating designation already exist.\nCheck the dates you have entered.'))

            region_tracker_ids = self.search(cr, uid, [('region_id','=',region_id),('end_date','>=',check_start_date), ('start_date','<',check_end_date)])
            if region_tracker_ids and len(region_tracker_ids) > 1:
                raise osv.except_osv(('Warning!!'),('Previous designation exist on this start date.\nCheck the dates you have entered.'))

        # hr_job_ids = hr_job_obj.search(cr, uid, [('desig_level','=','dos'),('model_id','=','dos')])
        # if hr_job_ids and len(hr_job_ids) > 1:
        #     raise osv.except_osv(_('Error !'),_("Please check job position. There have two records which have Heirarchy Level is DOS and  Designation Tracker Access is Region. Kindly change it or contact to Administrator"))
        # elif hr_job_ids:
        #     values.update({'designation_id': hr_job_ids[0]})
        #     values.update({'heirarchy_level': 'dos'})
        #     values.update({'covering_str_check': False,'covering_market_check': False,'covering_region_check': False,'store_name':False,'market_id':False})

        res = super(region_tracker, self).create(cr, uid, vals, context=context)
        if context:
            if sales_director:
                desig_id = designation_tracker_obj.create(cr, uid, values, context=context)
                if desig_id:
                    self.write(cr,uid,res,{'desig_id':desig_id})
                    track_ids = self.search(cr,uid,[('desig_id','=',desig_id),('id','=',res)])
                    if not track_ids:
                        cr.execute("update region_tracker set desig_id=%s where id=%s "%(desig_id,res))
         #####Sap tracker id takes a latest sap_tracker id
        if region_id:
            region_track_ids = self.search(cr, uid, [('region_id','=',region_id)],order = 'end_date desc')
            if region_track_ids:
                ext_company_id = self.browse(cr,uid,region_track_ids[0]).company_id.id
                ext_sale_mgr_id = self.browse(cr,uid,region_track_ids[0]).sales_director.id

                if ext_company_id:
                    market_region_obj.write(cr,uid,[region_id],{'company_id':ext_company_id})
                if ext_sale_mgr_id:
                    market_region_obj.write(cr,uid,[region_id],{'sales_director':ext_sale_mgr_id})
                else:
                    market_region_obj.write(cr,uid,[region_id],{'sales_director':False})
        return res      

    def write(self, cr, uid, ids, vals, context=None):
        hr_obj = self.pool.get('hr.employee')
        user_obj = self.pool.get('res.users')
        hr_job_obj = self.pool.get('hr.job')
        market_region_obj = self.pool.get('market.regions')
        designation_tracker_obj = self.pool.get('designation.tracker')
        self_data = self.browse(cr,uid,ids)
        values = {}
        if 'sales_director' in vals:
            sales_director = vals.get('sales_director')
        else:
            sales_director = self_data.sales_director.id or False

        if 'start_date' in vals:
            start_date = vals.get('start_date')
            check_start_date = datetime.datetime.strptime(vals.get('start_date' ), '%Y-%m-%d')
        else:
            start_date = self_data.start_date or False

        if 'end_date' in vals:
            end_date = vals.get('end_date')
            ext_end_date = self_data.end_date or False
        else:
            end_date = self_data.end_date or False

        if 'desig_id' in vals:
            desig_id = vals.get('desig_id')
        else:
            desig_id = self_data.desig_id.id or False

        if 'region_id' in vals:
            region_id = vals.get('region_id')
        else:
            region_id = self_data.region_id.id or False

        if 'company_id' in vals:
            company_id = vals.get('company_id')
        else:
            company_id = self_data.company_id.id or False

        if 'designation_id' in vals:
            designation_id = vals.get('designation_id',False)
        else:
            designation_id = self_data.designation_id.id or False

        if sales_director:
            values.update({'dealer_id': sales_director})
        if start_date:
            values.update({'start_date': start_date})
        if end_date:
            values.update({'end_date': end_date})
        if region_id:
            values.update({'region_id': region_id})
        if designation_id:
            values.update({'designation_id': designation_id})

        values.update({'heirarchy_level': 'dos', 'covering_str_check': False, 
            'covering_market_check':False,'covering_region_check':False,
            'store_name':False,'market_id':False})

        if isinstance(end_date, (str)):
            check_end_date = (datetime.datetime.strptime(end_date, '%Y-%m-%d'))
        else:
            check_end_date = end_date

        if isinstance(start_date, (str)):
            check_start_date = (datetime.datetime.strptime(start_date, '%Y-%m-%d'))
        else:
            check_start_date = start_date    
    #####Start date is greater than end date
        if context and check_start_date and check_end_date:
            if check_start_date > check_end_date:
                raise osv.except_osv(('Warning!!!'),('End date should be greater than start date. Check dates you have entered.'))

    #####Not allow user to enter designation for same period 
            region_tracker_ids = self.search(cr, uid, [('region_id','=',region_id),('start_date','<=',check_start_date),('end_date','>=',check_end_date)])
            if region_tracker_ids and len(region_tracker_ids) > 1:
                raise osv.except_osv(('Warning!!'),('Period for which you are updating designation already exist.\nCheck the dates you have entered.'))

            region_tracker_ids = self.search(cr, uid, [('region_id','=',region_id),('end_date','>=',check_start_date), ('start_date','<=',check_end_date)])
            if region_tracker_ids and len(region_tracker_ids) > 1:
                raise osv.except_osv(('Warning!!'),('Previous designation exist on this start date.\nCheck the dates you have entered.'))

        res = super(region_tracker, self).write(cr, uid, ids, vals, context=context)
        if context:
	    if sales_director:
                desig_id = designation_tracker_obj.create(cr, uid, values, context=context)
                if desig_id:
                    self.write(cr,uid,ids,{'desig_id':desig_id})
                    track_ids = self.search(cr,uid,[('desig_id','=',desig_id),('id','=',ids[0])])
                    if not track_ids:
                        cr.execute("update region_tracker set desig_id=%s where id=%s "%(desig_id,ids[0]))
            res = super(region_tracker, self).create(cr, uid, vals, context=context)
          
        #####End Handling for start date and end date 
            
            if region_id and company_id:
                market_region_obj.write(cr,uid,[region_id],{'company_id':company_id})
            if region_id:
                region_track_ids = self.search(cr, uid, [('region_id','=',region_id)],order = 'end_date desc')
                if region_track_ids:
                    ext_sale_mgr_id = self.browse(cr,uid,region_track_ids[0]).sales_director.id
                    ext_company_id = self.browse(cr,uid,region_track_ids[0]).company_id.id

                    if ext_company_id:
                        market_region_obj.write(cr,uid,[region_id],{'company_id':ext_company_id})
                    if ext_sale_mgr_id:
                        market_region_obj.write(cr,uid,[region_id],{'sales_director':ext_sale_mgr_id})
                    else:
                        market_region_obj.write(cr,uid,[region_id],{'sales_director':False})
        else:
            ext_region_ids = market_region_obj.search(cr,uid,[('sales_director','=',sales_director),('id','=',region_id)])
            if ext_region_ids and 'end_date' in vals:

                if ext_end_date and isinstance(ext_end_date, (str)):
                    ext_end_date = (datetime.datetime.strptime(ext_end_date, '%Y-%m-%d'))
                else:
                    ext_end_date = ext_end_date

                if isinstance(start_date, (str)):
                    ext_start_date = (datetime.datetime.strptime(start_date, '%Y-%m-%d'))
                else:
                    ext_start_date = end_date

                latest_region_tracker_ids = self.search(cr, uid, [('region_id','=',region_id)], order='end_date desc')

                if latest_region_tracker_ids:
                    latest_end_date = self.browse(cr,uid,latest_region_tracker_ids[0]).end_date
                    if latest_end_date and isinstance(latest_end_date, (str)):
                        latest_end_date = (datetime.datetime.strptime(latest_end_date, '%Y-%m-%d'))

                    if (latest_end_date and ext_end_date) and (latest_end_date < ext_end_date):
                        values = {
                        'start_date' :  check_end_date + datetime.timedelta(days=1),
                        'end_date' : check_end_date + datetime.timedelta(days=2192),####2190 days = 6 years                        
                        'region_id' : region_id,
                        'company_id':company_id,
                        }
                        self.create(cr,uid,values,context)

        if region_id and desig_id:
            dup_region_track_ids = self.search(cr, uid, [('region_id','=',region_id),('desig_id','=',desig_id)],order = 'id desc')
            if dup_region_track_ids and len(dup_region_track_ids)>1:
                self.unlink(cr,uid,dup_region_track_ids[0])

        if region_id:
            region_track_ids = self.search(cr, uid, [('region_id','=',region_id)],order = 'end_date desc')
            if region_track_ids:
                ext_company_id = self.browse(cr,uid,region_track_ids[0]).company_id.id
                ext_sale_mgr_id = self.browse(cr,uid,region_track_ids[0]).sales_director.id

                if ext_company_id:
                    market_region_obj.write(cr,uid,[region_id],{'company_id':ext_company_id})
                if ext_sale_mgr_id:
                    market_region_obj.write(cr,uid,[region_id],{'sales_director':ext_sale_mgr_id})
                else:
                    market_region_obj.write(cr,uid,[region_id],{'sales_director':False})       
        return res

region_tracker()


class ir_model_data(osv.osv):
    _inherit = 'ir.model.data'

ir_model_data()

class res_groups(osv.osv):
    """ jasper_groups are identify by following fields while 
        updating user's
        Created by Pratik
    """
    _name = "res.groups"
    _inherit = 'res.groups'
    _columns = {
        'jasper_check': fields.boolean('Jasper Active',
                    help="Group created to set access rights for Jasper Server."),
        'group_tenantId': fields.char('Jasper Group tenantId'),
    }
    _defaults = {
                'jasper_check':False
    }
res_groups()

class update_saleentry_records(osv.osv):
    _name = "update.saleentry.records"
    _columns = {
               'market_id':fields.many2one('market.place','Market'),
               'store_id': fields.many2one('sap.store','Store'),
               'employee_id': fields.many2one('hr.employee','Sales Representative'),
               'region_id': fields.many2one('market.regions','Regions'),
               'start_date': fields.date('Start Date'),
               'end_date': fields.date('End Date'),
               'state': fields.selection([
                    ('draft','Draft'),
                    ('done','Done'),
                    ],'State'),
                'update_message': fields.text('Update Message'),
                'records_count': fields.integer('Count'),
                'product_id':fields.many2many('product.product','update_dsr_product_rel','update_id','prod_id','Products'),
                'dsr_write_date':fields.date('Write Date'),
                'product_type':fields.many2many('product.category','update_dsr_prod_type_rel','update_id','prod_type_id','Product Type'),
                'notes':fields.text('Reason For Update')
            }

    """Note to be displayed to Feature at down time"""

    def _get_update_message_note(self, cr, uid, ids, context=None):
        text = "NOTE: This Feature must be run in down time only"
        return text

    _defaults={
            'state':'draft',
            'update_message': _get_update_message_note,
    }

    def update_records(self,cr,uid,ids,context=None):
        update_id= self.browse(cr,uid,ids[0])
        write_vals = {}
        dsr_ids = []
        update_start_date= update_id.start_date
        update_end_date = update_id.end_date
        update_store_id = update_id.store_id.id
        update_market_id = update_id.market_id.id
        update_region_id = update_id.region_id.id
        update_employee_id = update_id.employee_id.id
        if update_id.product_id:
            cr.execute("select prod_id from update_dsr_product_rel where update_id = %s"%(update_id.id))
            prod_id = map(lambda x: x[0], cr.fetchall())
            condition_string = str("")
            if len(prod_id) == 1:
                condition_string += str(" = %s"%(prod_id[0]))
            else:
                condition_string += str(" in %s"%(tuple(prod_id),))
            cr.execute("select distinct(product_id) from wireless_dsr_postpaid_line where dsr_product_code"+condition_string+" and dsr_act_date between %s and %s",(update_start_date,update_end_date))
            dsr_ids = map(lambda x: x[0], cr.fetchall())
            cr.execute("select distinct(product_id) from wireless_dsr_upgrade_line where dsr_product_code"+condition_string+" and dsr_act_date between %s and %s",(update_start_date,update_end_date))
            upgrade_data = cr.fetchall()
            for upgrade_data_each in upgrade_data:
                dsr_ids.append(upgrade_data_each[0])
            cr.execute("select distinct(product_id) from wireless_dsr_prepaid_line where dsr_product_description"+condition_string+" and dsr_act_date between %s and %s",(update_start_date,update_end_date))
            upgrade_data = cr.fetchall()
            for upgrade_data_each in upgrade_data:
                dsr_ids.append(upgrade_data_each[0])
            dsr_ids = list(set(dsr_ids))
            cr.execute("select distinct(feature_product_id) from wireless_dsr_feature_line where dsr_product_code"+condition_string+" and dsr_act_date between %s and %s",(update_start_date,update_end_date))
            upgrade_data = cr.fetchall()
            for upgrade_data_each in upgrade_data:
                dsr_ids.append(upgrade_data_each[0])
            dsr_ids = list(set(dsr_ids))
        if update_id.product_type:
            cr.execute("select prod_type_id from update_dsr_prod_type_rel where update_id = %s"%(update_id.id))
            prod_type_id = map(lambda x: x[0], cr.fetchall())
            condition_string = str("")
            if len(prod_type_id) == 1:
                condition_string += str(" = %s"%(prod_type_id[0]))
            else:
                condition_string += str(" in %s"%(tuple(prod_type_id),))
            cr.execute("select distinct(product_id) from wireless_dsr_postpaid_line where dsr_product_type"+condition_string+" and dsr_act_date between %s and %s",(update_start_date,update_end_date))
            dsr_ids = map(lambda x: x[0], cr.fetchall())
            cr.execute("select distinct(product_id) from wireless_dsr_upgrade_line where dsr_product_type"+condition_string+" and dsr_act_date between %s and %s",(update_start_date,update_end_date))
            upgrade_data = cr.fetchall()
            for upgrade_data_each in upgrade_data:
                dsr_ids.append(upgrade_data_each[0])
            cr.execute("select distinct(product_id) from wireless_dsr_prepaid_line where dsr_product_type"+condition_string+" and dsr_act_date between %s and %s",(update_start_date,update_end_date))
            upgrade_data = cr.fetchall()
            for upgrade_data_each in upgrade_data:
                dsr_ids.append(upgrade_data_each[0])
            dsr_ids = list(set(dsr_ids))
            cr.execute("select distinct(feature_product_id) from wireless_dsr_feature_line where dsr_product_type"+condition_string+" and dsr_act_date between %s and %s",(update_start_date,update_end_date))
            upgrade_data = cr.fetchall()
            for upgrade_data_each in upgrade_data:
                dsr_ids.append(upgrade_data_each[0])
            dsr_ids = list(set(dsr_ids))
        where_condition=[]
        where_condition.append(('dsr_date', '>=', update_start_date))
        where_condition.append(('dsr_date', '<=', update_end_date))
        where_condition.append(('state','=','done'))
        if update_store_id:
            where_condition.append(('dsr_store_id', '=', update_store_id))
        if update_market_id:
            where_condition.append(('dsr_market_id', '=', update_market_id))
        if update_region_id:
            where_condition.append(('dsr_region_id', '=', update_region_id))
        if update_employee_id:
            where_condition.append(('dsr_sales_employee_id', '=', update_employee_id))
        if update_id.product_id:
            where_condition.append(('id','in',dsr_ids))
        if update_id.dsr_write_date:
            where_condition.append(('write_date','>=',update_id.dsr_write_date))
        if update_id.product_type:
            where_condition.append(('id','in',dsr_ids))
        wireless_dsr_obj=self.pool.get('wireless.dsr')
        wireless_dsr_search=wireless_dsr_obj.search(cr,uid,where_condition)
        count = 0
        logger.error("Found DSR records to update:%s"%(len(wireless_dsr_search)))
        for wireless_dsr_browse in wireless_dsr_obj.browse(cr,uid,wireless_dsr_search):
            main_wireless_dsr_id = wireless_dsr_browse.id
            if wireless_dsr_browse.postpaid_product_line:
                write_vals.update({'postpaid_product_line':[]})
                for postpaid_id in wireless_dsr_browse.postpaid_product_line:
                    write_vals['postpaid_product_line'].append([1,postpaid_id.id,{'customer_name':postpaid_id.customer_name+' '}])
            if wireless_dsr_browse.upgrade_product_line:
                write_vals.update({'upgrade_product_line':[]})
                for upgrade_id in wireless_dsr_browse.upgrade_product_line:
                    write_vals['upgrade_product_line'].append([1,upgrade_id.id,{'customer_name':upgrade_id.customer_name+' '}])
            if wireless_dsr_browse.feature_product_line:
                write_vals.update({'feature_product_line':[]})
                for feature_id in wireless_dsr_browse.feature_product_line:
                    write_vals['feature_product_line'].append([1,feature_id.id,{'customer_name':feature_id.customer_name+' '}])
            if wireless_dsr_browse.prepaid_product_line:
                write_vals.update({'prepaid_product_line':[]})
                for prepaid_id in wireless_dsr_browse.prepaid_product_line:
                    write_vals['prepaid_product_line'].append([1,prepaid_id.id,{'customer_name':prepaid_id.customer_name+' '}])
            if wireless_dsr_browse.acc_product_line:
                write_vals.update({'acc_product_line':[]})
                for accessory_id in wireless_dsr_browse.acc_product_line:
                    write_vals['acc_product_line'].append([1,accessory_id.id,{'customer_name':accessory_id.customer_name+' '}])
            try:
                wireless_dsr_obj.write(cr,uid,main_wireless_dsr_id,write_vals)
            except:
                logger.error("Written valss:%s"%(main_wireless_dsr_id))
            count = count +1
            logger.error("Count :%s"%(count))
        logger.error("Complete Update for %s records count %s"%(update_start_date,len(wireless_dsr_search)))
        self.write(cr, uid, ids, {'state':'done','records_count':len(wireless_dsr_search)})
        return True

update_saleentry_records()