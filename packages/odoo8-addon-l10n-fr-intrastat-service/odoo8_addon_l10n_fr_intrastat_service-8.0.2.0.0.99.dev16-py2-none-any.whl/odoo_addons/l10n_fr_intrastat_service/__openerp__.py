# -*- coding: utf-8 -*-
##############################################################################
#
#    l10n FR intrastat service module for Odoo (DES)
#    Copyright (C) 2010-2015 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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
    'name': 'France Intrastat Service',
    'version': '8.0.2.0.0',
    'category': 'Localisation/Report Intrastat',
    'license': 'AGPL-3',
    'summary': 'Module for Intrastat service reporting (DES) for France',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'depends': ['intrastat_base'],
    'data': [
        'security/ir.model.access.csv',
        'intrastat_service_view.xml',
        'intrastat_service_reminder.xml',
        'security/intrastat_service_security.xml',
    ],
    'demo': ['intrastat_demo.xml'],
    'installable': True,
    'application': True,
}
