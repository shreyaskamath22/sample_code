
{
    'name': 'Employee Education Records',
    'version': '1.0',
    'category': 'Generic Modules/Human Resources',
    'description': """
Details About Employee Education and Job
======================================

    Add an extra field about an employee's education.
    """,
    'author': 'ujwala pawade <ujwalahpawade@gmail.com>',
    'website': 'http://www.zeeva.com',
    'depends': [
        'hr', 'base'
    ],
    'init_xml': [
    ],
    'update_xml': [
        'security/ir.model.access.csv',
        'hr_view.xml',
    ],
    'test': [
    ],
    'demo_xml': [
    ],
    'installable': True,
    'active': False,
}
