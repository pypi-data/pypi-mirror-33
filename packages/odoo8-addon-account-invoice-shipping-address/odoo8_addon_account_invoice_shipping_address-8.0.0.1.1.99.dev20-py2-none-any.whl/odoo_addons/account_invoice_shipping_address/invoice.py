# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Domsense s.r.l. (<http://www.domsense.com>).
#    Copyright (C) 2013 Andrea Cometa Perito Informatico (www.andreacometa.it)
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

from openerp.osv import fields, orm


class account_invoice(orm.Model):
    _inherit = "account.invoice"

    _columns = {
        'address_shipping_id': fields.many2one(
            'res.partner',
            'Shipping Address',
            readonly=True,
            states={
                'draft': [('readonly', False)],
                'sent': [('readonly', False)]
            },
            help="Delivery address for current invoice."),
    }
