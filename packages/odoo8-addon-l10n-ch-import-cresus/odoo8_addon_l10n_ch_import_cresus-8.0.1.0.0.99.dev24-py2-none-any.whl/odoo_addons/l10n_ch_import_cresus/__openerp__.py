# -*- coding: utf-8 -*-
##############################################################################
#
#    Author Vincent Renaville
#    Copyright 2015 Camptocamp SA
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
    'name': 'Account Import Cresus',
    'version': '8.0.1.0.0',
    'depends': [
        'account',
    ],
    'author': 'Camptocamp, Odoo Community Association (OCA)',
    'website': 'http://www.camptocamp.com',
    'data': [
        'wizard/l10n_ch_import_cresus_view.xml',
        'account_tax_view.xml',
        'menu.xml',
    ],
    'installable': True,
}
