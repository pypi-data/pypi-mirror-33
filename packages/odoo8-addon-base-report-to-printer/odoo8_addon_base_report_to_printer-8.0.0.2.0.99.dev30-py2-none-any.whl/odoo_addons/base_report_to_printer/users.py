# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2007 Ferran Pegueroles <ferran@pegueroles.com>
#    Copyright (c) 2009 Albert Cervera i Areny <albert@nan-tic.com>
#    Copyright (C) 2011 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2011 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2013-2014 Camptocamp (<http://www.camptocamp.com>)
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields

from .printing import _available_action_types


class res_users(models.Model):
    """
    Users
    """
    _name = 'res.users'
    _inherit = 'res.users'

    def _user_available_action_types(self):
        return [(code, string) for code, string
                in _available_action_types(self)
                if code != 'user_default']

    printing_action = fields.Selection(_user_available_action_types)
    printing_printer_id = fields.Many2one(comodel_name='printing.printer',
                                          string='Default Printer')
