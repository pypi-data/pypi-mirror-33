# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
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
    'name': "Purchase partial invoicing",
    'version': '8.0.0.1.2',
    'category': 'Purchase Management',
    'author': "Agile Business Group,"
              "ACSONE SA/NV,"
              "Odoo Community Association (OCA)",
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    "depends": ['purchase',
                'base_suspend_security'],
    "data": [
        'wizard/po_line_invoice_view.xml',
        'wizard/po_line_cancel_quantity_view.xml',
        'purchase_view.xml',
    ],
    "demo": [],
    "active": False,
    "installable": True
}
