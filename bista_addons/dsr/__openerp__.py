{
    'name' : 'Wirelessvision DSR Process',
    'version' : '1.0',
    'depends' : ['wirelessvision','wirelessvision_extra','product'],
    'author' : 'Bista Solutions Pvt. Ltd.',
    'category': 'Sale',
    'description': """
This module describes DSR Process.
    """,
    'website': 'http://www.openerp.com',
    'demo': [],
    'data': [
    'security/dsr_security.xml',
    'security/ir.model.access.csv',
    # 'security/jasper_view_update.xml',
    'wizard/void_wizard_view.xml',
    'menu_hide.xml',
    'dsr_view.xml',
    'wizard/dsr_manually_update_view.xml',
    'dsr_sequence.xml',
    'wizard/update_acc_qty_view.xml'
#    'res_partner_view.xml',
    ],
    'css': ['static/src/css/tree_width_css.css'],
    'qweb':['static/src/xml/base.xml'],
    'installable': True,
    'auto_install': False,
}
