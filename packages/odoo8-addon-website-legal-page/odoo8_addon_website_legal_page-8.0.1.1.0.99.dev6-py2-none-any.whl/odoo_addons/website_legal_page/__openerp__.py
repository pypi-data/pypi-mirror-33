# -*- coding: utf-8 -*-
# Python source code encoding : https://www.python.org/dev/peps/pep-0263/
##############################################################################
#
#    OpenERP, Odoo Source Management Solution
#    Copyright (c) 2015 Antiun Ingeniería S.L. (http://www.antiun.com)
#                       Antonio Espinosa <antonioea@antiun.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name': "Website legal page",
    'category': 'Website',
    'version': '8.0.1.1.0',
    'depends': [
        'website',
    ],
    'data': [
        'views/reusable_templates.xml',
        'views/website_legal.xml',
        'views/website_privacy.xml',
        'views/website_terms.xml',
    ],
    'author': 'Antiun Ingeniería S.L., '
              'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'http://www.tecnativa.com',
    'license': 'AGPL-3',
    'demo': [],
    'test': [],
    'installable': True,
}
