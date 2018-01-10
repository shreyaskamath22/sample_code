{
    'name' : 'Wirelessvision Document Management System Patch',
    'version' : '1.0',
    'depends' : ['base','document','email_template','hr','wirelessvision_dms_config'],
    'author' : 'Bista Solutions Pvt. Ltd.',
    'category': 'document',
    'description': """
This module customize existing Document Management System and make it configurable access rights.
    """,
    'website': 'http://www.bistasolutions.com',
    'demo': [],
    'data': [
    'ir_attachment_view.xml',
    'document_view.xml',
    'security/dsm_security.xml',
    'security/ir.model.access.csv',    
    ],
    'installable': True,
    'auto_install': False,
    'images': [],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
