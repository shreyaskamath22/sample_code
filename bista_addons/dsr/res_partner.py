# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv

class res_users(osv.osv):

    _inherit = 'res.users'

    _columns = {
        'email_id':fields.related('partner_id', 'email', type='char', string='Email',store=True),
    }

res_users()
