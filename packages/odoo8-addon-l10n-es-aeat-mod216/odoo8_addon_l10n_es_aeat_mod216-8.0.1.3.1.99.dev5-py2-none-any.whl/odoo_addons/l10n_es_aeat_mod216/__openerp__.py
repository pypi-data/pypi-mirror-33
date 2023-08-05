# -*- encoding: utf-8 -*-
##############################################################################
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'AEAT modelo 216',
    'version': '8.0.1.3.1',
    'category': "Localisation/Accounting",
    'author': "Serv. Tecnol. Avanzados - Pedro M. Baeza,"
              "AvanzOSC,"
              "Antiun Ingeniería S.L.,"
              "Odoo Community Association (OCA)",
    'website': "https://github.com/OCA/l10n-spain",
    'license': 'AGPL-3',
    'depends': [
        'l10n_es_aeat',
        'l10n_es_aeat_mod111',
    ],
    'data': [
        'wizard/export_mod216_to_boe.xml',
        'views/mod216_view.xml',
        'views/res_partner_view.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml'
    ],
    'installable': True,
}
