# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
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

{'name': 'Sale Payment Method - Automatic Worflow (link module)',
 'version': '8.0.1.0.0',
 'author': 'Camptocamp,Akretion,Odoo Community Association (OCA)',
 'license': 'AGPL-3',
 'category': 'Generic Modules/Others',
 'depends': ['sale_payment_method',
             'sale_automatic_workflow'],
 'website': 'http://www.camptocamp.com',
 'data': ['view/sale_order_view.xml',
          'view/payment_method_view.xml',
          ],
 'test': [],
 'installable': True,
 'auto_install': True,
 }
