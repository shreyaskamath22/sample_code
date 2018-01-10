# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Employee Confirmation',
    'version': '1.0',
    'category': 'Human Resources',
    'description': """

Employee Confirmation Module
========================

    """,
    'author': 'ujwala pawade',
    'website': 'http://www.zeeva.com',
    'license': 'AGPL-3',
    'depends': ['hr', 'base'],
    'data': [
        'hr_view.xml',
        'hr_employee_profile_setup_data.xml',
        'hr_employee_confirmation_report.xml',
        'hr_confirmation_data.xml',
        'confirmation_email_templates.xml',
        'employee_confirmation_scheduler.xml',
	    'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'images': [],
}
