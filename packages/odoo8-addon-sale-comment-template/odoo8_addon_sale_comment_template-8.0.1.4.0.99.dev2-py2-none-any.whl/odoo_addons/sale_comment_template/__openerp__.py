# -*- coding: utf-8 -*-
#
#
#    Author: Nicolas Bessi
#    Copyright 2013-2014 Camptocamp SA
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
#
{"name": "Sale Comments",
 "summary": "Comments texts templates on Sale documents",
 "version": "8.0.1.4.0",
 "depends": ["sale",
             "invoice_comment_template",
             ],
 "author": "Camptocamp,Odoo Community Association (OCA)",
 "license": "AGPL-3",
 "data": ["sale_order_view.xml",
          'base_comment_template_view.xml',
          'views/report_saleorder.xml',
          'security/ir.model.access.csv',
          ],
 "category": "Sale",
 "installable": True,
 }
