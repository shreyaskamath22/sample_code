from report import report_sxw
import time
from tools import amount_to_text
from tools.amount_to_text import amount_to_text_in
from corporate_address import *
class summary_of_accounts(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(summary_of_accounts, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
			'time': time,
			'amount_to_text_in': amount_to_text_in,
			'amount_in_rupees': self.amount_in_rupees,
			'get_account_name': self.get_account_name,
			'get_branch_addr' : self.get_branch_addr,
			'closing_balance_calc':self.closing_balance_calc,
            'get_current_time':self.get_current_time,
        })
    def closing_balance_calc(self,closing_amount):
        if float(closing_amount) > 0:
            return str("%.2f" % abs(closing_amount))+' Dr'
        elif  float(closing_amount) < 0:
            return str("%.2f" % abs(closing_amount))+' Cr'
        
    def get_branch_addr(self,self_id):    	
	return get_branch_addr(self,self_id)

    def amount_in_rupees(self,amount):
        if amount >= 1 :
                amt_str=amount_to_text_in(amount,'')
                return 'Rupee '+amt_str
        else :  
                amt_str=amount_to_text_in(amount,'')
                return amt_str[8:-5]+ 'Paise Only'
                
    def get_account_name(self,self_id,to_date):
        cr = self.cr
        uid = self.uid
        dic = {
            'iob_one_1':'',
            'iob_one_2':'',
            'iob_two':'',
             }

        for res in self.pool.get('monthly.report').browse(cr,uid,[self_id]):
                name = []
                search_name = self.pool.get('account.account').search(cr,uid,[('account_selection','in',('iob_one','iob_two')),('create_date','<=',to_date)])
                search_name.reverse()
                for nm in self.pool.get('account.account').browse(cr,uid,search_name):
                        if nm.receive_bank_no == 'bank_one':
                                dic['iob_one_1'] = nm.name
                        if nm.receive_bank_no == 'bank_two':
                                dic['iob_one_2'] = nm.name
                        if nm.receive_bank_no == 'bank_three':
                                dic['iob_one_3'] = nm.name
                        if not nm.receive_bank_no:
                                dic['iob_two'] = nm.name

                return dic
            
    def get_current_time(self):
        return get_current_time(self)

report_sxw.report_sxw('report.psd.summary.accounts', 'monthly.report', 'PSD_branch/addons_branch/psd_accounting/report/summary_of_accounts.rml', parser=summary_of_accounts, header=False)
