# -*- encoding: utf-8 -*-
##############################################################################
#
#    (c) 2015 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#             Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

{
    "name": "Tax chart for a period interval",
    "version": "8.0.1.0.0",
    "depends": [
        "account",
    ],
    "author": "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              'Antiun Ingeniería S.L., '
              'Odoo Community Association (OCA)',
    "website": "http://www.antiun.com",
    "contributors": [
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
    ],
    "category": "Accounting & Finance",
    "data": [
        'wizard/account_tax_chart_view.xml',
    ],
    "installable": True,
}
