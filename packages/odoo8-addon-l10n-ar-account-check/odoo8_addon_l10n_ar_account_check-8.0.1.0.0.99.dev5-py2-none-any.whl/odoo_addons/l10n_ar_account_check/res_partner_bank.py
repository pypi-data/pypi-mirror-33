# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2008-2011  Thymbra
#    Copyright (c) 2011-2014 E-MIPS (http://www.e-mips.com.ar)
#    Copyright (c) 2014 Aconcagua Team (http://www.proyectoaconcagua.com.ar)
#    All Rights Reserved. See AUTHORS for details.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
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

from openerp import models, fields, api


class res_partner_bank(models.Model):
    _name = 'res.partner.bank'
    _inherit = 'res.partner.bank'

    account_id = fields.Many2one('account.account', 'Account')

res_partner_bank()
