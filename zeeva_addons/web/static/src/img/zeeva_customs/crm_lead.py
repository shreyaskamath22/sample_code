# -*- coding: utf-8 -*-

from openerp.osv import fields,osv
from openerp.tools.translate import _
import tools
from openerp.addons.base_status.base_stage import base_stage
from base.res.res_partner import format_address
from openerp import SUPERUSER_ID

class crm_lead(base_stage, format_address, osv.osv):
    """ CRM Lead Case """
    
    _inherit = 'crm.lead'
    
    _columns = {
        #'name': fields.char('Subject', size=64, required=False, select=1),
        'website': fields.char('Website', size=128),
        'prod_categ_ids': fields.many2many('product.category', 'crm_lead_product_category_rel', 'lead_id', 'product_category_id', 'Product categories'),
    }
    
    _defaults = {
        'opt_out': True,
        'user_id': False,
    }
    
    def _lead_create_contact(self, cr, uid, lead, name, is_company, parent_id=False, context=None):
        partner = self.pool.get('res.partner')
        vals = {'name': name,
            'user_id': lead.user_id.id,
            'comment': lead.description,
            'section_id': lead.section_id.id or False,
            'parent_id': parent_id,
            'phone': lead.phone,
            'mobile': lead.mobile,
            'email': lead.email_from and tools.email_split(lead.email_from)[0],
            'fax': lead.fax,
            'title': lead.title and lead.title.id or False,
            'function': lead.function,
            'street': lead.street,
            'street2': lead.street2,
            'zip': lead.zip,
            'city': lead.city,
            'country_id': lead.country_id and lead.country_id.id or False,
            'state_id': lead.state_id and lead.state_id.id or False,
            'is_company': is_company,
            'customer': True,
            'supplier': False,
            'type': 'contact',
            'website': lead.website
        }
        partner = partner.create(cr, uid, vals, context=context)
        return partner
    
    def redirect_opportunity_view(self, cr, uid, opportunity_id, context=None):
        models_data = self.pool.get('ir.model.data')

        # Get opportunity views
        dummy, form_view = models_data.get_object_reference(cr, uid, 'zeeva_customs', 'zeeva_crm_opportunity_form_view')
        dummy, tree_view = models_data.get_object_reference(cr, uid, 'crm', 'crm_case_tree_view_oppor')
        return {
            'name': _('Opportunity'),
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'crm.lead',
            'domain': [('type', '=', 'opportunity')],
            'res_id': int(opportunity_id),
            'view_id': False,
            'views': [(form_view or False, 'form'),
                    (tree_view or False, 'tree'),
                    (False, 'calendar'), (False, 'graph')],
            'type': 'ir.actions.act_window',
        }
        
    # OVERWRITE of the function to avoid sending wrong emails to leads and potential customers
    def message_get_suggested_recipients(self, cr, uid, ids, context=None):
        """ Returns suggested recipients for ids. Those are a list of
            tuple (partner_id, partner_name, reason), to be managed by Chatter. """
        result = dict.fromkeys(ids, list())
        if self._all_columns.get('user_id'):
            for obj in self.browse(cr, SUPERUSER_ID, ids, context=context):  # SUPERUSER because of a read on res.users that would crash otherwise
                if not obj.user_id or not obj.user_id.partner_id:
                    continue
                #self._message_add_suggested_recipient(cr, uid, result, obj, partner=obj.user_id.partner_id, reason=self._all_columns['user_id'].column.string, context=context)
        #print result
        return result
    
    #def message_get_suggested_recipients(self, cr, uid, ids, context=None):
        ##recipients = super(crm_lead, self).message_get_suggested_recipients(cr, uid, ids, context=context)
        #try:
            #for lead in self.browse(cr, uid, ids, context=context):True
                ##if lead.partner_id:
                    ##self._message_add_suggested_recipient(cr, uid, recipients, lead, partner=lead.partner_id, reason=_('Customer'))
                ##elif lead.email_from:
                    ##self._message_add_suggested_recipient(cr, uid, recipients, lead, email=lead.email_from, reason=_('Customer Email'))
        #except (osv.except_osv, orm.except_orm):  # no read access rights -> just ignore suggested recipients because this imply modifying followers
            #pass
        #print recipients or ''
        #return recipients or ''
        
crm_lead()

class crm_meeting(osv.osv):
    _inherit = 'crm.meeting'
    
    _columns ={
        
    }
    
    #def view_manual(self, cr, uid, ids, context=None):
        
        #final_url = "http://docs.google.com/viewer?url=erp.zeeva.com%3A8069%2Fzeeva_customs%2Fstatic%2Fsrc%2Fpdf%2Fmanual.pdf"
        
        #return {
            #'type': 'ir.actions.act_url',
            #'url': final_url,
            #'target': 'new'
        #}
        
crm_meeting()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
