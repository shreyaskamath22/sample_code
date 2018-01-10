{
    'name' : 'Wirelessvision Sale Commission',
    'version' : '1.0',
    'depends' : ['base','wirelessvision_crash'],
    'author' : 'Bista Solutions Pvt. Ltd.',
    'category': 'Human Resources',
    'description': """
This module describes Employee Purchase Plan Process.
    """,
    'website': 'http://www.openerp.com',
    'demo': [],
    'data': [
    # 'security/salescommission_security.xml',
    'security/ir.model.access.csv',
    'report/transactions_report_view.xml',
    'sales_commission_view.xml',
    'packaged_commission_view.xml',
    'wizard/package_comm_script_view.xml',
    'wizard/market_region_reset_view.xml',
    'cron/jasper_cron_data.xml'
    ],
    'css': ['static/src/css/base_css.css'],
    'installable': True,
    'auto_install': False,
    'images': [],
}
