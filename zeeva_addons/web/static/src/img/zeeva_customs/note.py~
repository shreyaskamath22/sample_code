# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.osv import osv, fields


class note_note(osv.osv):
    
    _inherit = 'note.note'
    
    _columns ={
        
    }
    
    def message_subscribe_users(self, cr, uid, ids, user_ids=None, subtype_ids=None, context=None):
        """ Wrapper on message_subscribe, using users. If user_ids is not
            provided, subscribe uid instead. """
        if user_ids is None:
            user_ids = [uid]
        partner_ids = [user.partner_id.id for user in self.pool.get('res.users').browse(cr, uid, user_ids, context=context)]
        return self.message_subscribe(cr, uid, ids, partner_ids, subtype_ids=subtype_ids, context=context)
    
    def message_subscribe(self, cr, uid, ids, partner_ids, subtype_ids=None, context=None):
        """ Add partners to the records followers. """
                
        result = super(note_note,self).message_subscribe(cr, uid, ids, partner_ids, subtype_ids=subtype_ids, context=context)
        
        p_uid = self.pool.get('res.users').browse(cr, uid, uid, context=context).partner_id.id
        
        if result and p_uid not in partner_ids: #user added to the follower list
        
            #set the stage of the current note at the first stage of each new follower
            for p in partner_ids:
                #get the user ID of the new follower
                user_partner_id = self.pool.get('res.partner').browse(cr, uid, p, context=context).user_ids[0].id
                
                #get the stage IDs of the new follower
                current_stage_ids = self.pool.get('note.stage').search(cr,SUPERUSER_ID,[('user_id','=',user_partner_id)], context=context)
                
                #set the stage of the current note at the first stage of the current new follower
                if current_stage_ids:
                    res = self.write(cr,SUPERUSER_ID,ids[0],{'stage_ids':[(4,current_stage_ids[0])]})
                
        return True
    
    #def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False):
        
        #if groupby and groupby[0]=="stage_id":
            ##search all stages
            #current_stage_ids = self.pool.get('note.stage').search(cr,uid,[('user_id','=',uid)], context=context)

            #if current_stage_ids: #if the user have some stages
                ##dict of stages: map les ids sur les noms
                #stage_name = dict(self.pool.get('note.stage').name_get(cr, uid, current_stage_ids, context=context))

                #result = [{ #notes by stage for stages user
                        #'__context': {'group_by': groupby[1:]},
                        #'__domain': domain + [('stage_ids.id', '=', current_stage_id)],
                        #'stage_id': (current_stage_id, stage_name[current_stage_id]),
                        #'stage_id_count': self.search(cr,uid, domain+[('stage_ids', '=', current_stage_id)], context=context, count=True)
                    #} for current_stage_id in current_stage_ids]

                ##note without user's stage
                #nb_notes_ws = self.search(cr,uid, domain+[('stage_ids', 'not in', current_stage_ids)], context=context, count=True)
                    
                #if nb_notes_ws:
                    ##force add the first stage of the current user as the stage of this new note
                    #for n in self.search(cr,uid, domain+[('stage_ids', 'not in', current_stage_ids)], context=context, count=False):
                        #self.write(cr,uid,n,{'stage_id':current_stage_ids[0]})
                    
                    ## add note to the first column if it's the first stage
                    #dom_not_in = ('stage_ids', 'not in', current_stage_ids)
                    #if result and result[0]['stage_id'][0] == current_stage_ids[0]:
                        #dom_in = result[0]['__domain'].pop()
                        #result[0]['__domain'] = domain + ['|', dom_in, dom_not_in]
                    #else:
                        ## add the first stage column
                        #result = [{
                            #'__context': {'group_by': groupby[1:]},
                            #'__domain': domain + [dom_not_in],
                            #'stage_id': (current_stage_ids[0], stage_name[current_stage_ids[0]]),
                            #'stage_id_count':nb_notes_ws
                        #}] + result

            #else: # if stage_ids is empty

                ##note without user's stage
                #nb_notes_ws = self.search(cr,uid, domain, context=context, count=True)
                #if nb_notes_ws:
                    #result = [{ #notes for unknown stage
                        #'__context': {'group_by': groupby[1:]},
                        #'__domain': domain,
                        #'stage_id': False,
                        #'stage_id_count':nb_notes_ws
                    #}]
                #else:
                    #result = []
            #return result

        #else:
            #return super(note_note, self).read_group(self, cr, uid, domain, fields, groupby, 
                #offset=offset, limit=limit, context=context, orderby=orderby)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
