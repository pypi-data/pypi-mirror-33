# -*- coding: utf-8 -*-
##############################################################################
#
#    Author:  Alexandre Fayolle
#    Copyright 2012 Camptocamp SA
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
    'name': 'Replenishment Cost',
    'version': '9.0.1.0.0',
    'author': "Camptocamp,GRAP,Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'category': 'Products',
    'depends': [
        'product',
    ],
    'website': 'http://www.camptocamp.com/',
    'data': [
        'views/product_view.xml',
        'demo/res_groups.yml',
    ],
    'test': [
        'test/cost_price_update.yml',
    ],
    'installable': True,
}
