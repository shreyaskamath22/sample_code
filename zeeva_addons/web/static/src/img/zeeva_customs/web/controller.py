# -*- coding: utf-8 -*-

from openerp.tools.translate import _
import operator

import openerp.addons.web.http as http
import openerp.addons.web.controllers.main as main
openerpweb = http

import openerp
import re
from openerp.modules.registry import RegistryManager
from openerp.addons.auth_signup.res_users import SignupError
import openerp.addons.auth_signup.controllers.main as auth_main

class Session2(main.Session):
    _cp_path = "/web/session"

    @openerpweb.jsonrequest
    def change_password (self,req,fields):
        #print "\nTOTO\n"
        old_password, new_password,confirm_password = operator.itemgetter('old_pwd', 'new_password','confirm_pwd')(
                dict(map(operator.itemgetter('name', 'value'), fields)))
                
        if not (old_password.strip() and new_password.strip() and confirm_password.strip()):
            return {'error':_('You cannot leave any password empty.'),'title': _('Change Password Warning')}
            
        if new_password != confirm_password:
            return {'error': _('The new password and its confirmation must be identical.'),'title': _('Change Password Warning')}
            
        try:            
            # Try to change the password
            res = req.session.model('res.users').change_password(old_password, new_password)
            
            # result is True if OK, or a string message if problem
            if res == True:
                return {'new_password':new_password}
                
            elif res == "too short":
                return {'error': _('Password must be at least 8 characters long!'), 'title': _('Change Password Error')}
                
            elif res == "no numbers":
                return {'error': _('Password must have numbers!'), 'title': _('Change Password Error')}
                
            elif res == "no letters":
                return {'error': _('Password must have letters!'), 'title': _('Change Password Error')}
        
        # if old password is wrong, Exception on login credentials is raised
        except Exception:
            return {'error': _('The old password you provided is incorrect, your password was not changed.'), 'title': _('Change Password Warning')}
            
        return {'error': _('Error, password not changed !'), 'title': _('Change Password Warning')}
        
        
class Controller2(auth_main.Controller):
    _cp_path = '/auth_signup'

    @http.jsonrequest
    def signup(self, req, dbname, token, **values):
        """ sign up a user (new or existing)"""
        
        # CHECK PASSWORD
        password = values.get('password')
        if len(password) < 8:
            return {'error': _('Password must be at least 8 characters long!'), 'title': _('Change Password Error')}
        
        if not re.search('\d+',password):
            return {'error': _('Password must have numbers!'), 'title': _('Change Password Error')}
        
        if not (re.search('[a-z]+',password) or re.search('[A-Z]+',password)):
            return {'error': _('Password must have letters!'), 'title': _('Change Password Error')}
        
        try:
            self._signup_with_values(req, dbname, token, values)
        except SignupError, e:
            return {'error': openerp.tools.exception_to_unicode(e)}
        return {}

    def _signup_with_values(self, req, dbname, token, values):
        registry = RegistryManager.get(dbname)
        with registry.cursor() as cr:
            res_users = registry.get('res.users')
            res_users.signup(cr, openerp.SUPERUSER_ID, values, token)

# vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4:
