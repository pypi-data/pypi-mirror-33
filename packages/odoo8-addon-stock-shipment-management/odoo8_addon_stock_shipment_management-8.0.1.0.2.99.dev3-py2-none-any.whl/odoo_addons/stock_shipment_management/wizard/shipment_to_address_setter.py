# -*- coding: utf-8 -*-
#
#
#    Author: Yannick Vaucher
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
#    GNU Affero General Public License for more description.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
from openerp import models, fields, api


class ToAddressSetter(models.TransientModel):
    _name = "shipment.to_address.setter"
    _inherit = "shipment.value.setter"

    to_address_id = fields.Many2one(
        'res.partner',
        'To Address',
        help="Shipment To Address"
    )

    @api.multi
    def set_value(self):
        """ Changes the Shipment To Address and update departure and arrival
        pickings """
        self.ensure_one()
        self.shipment_id.to_address_id = self.to_address_id
        pickings = self.shipment_id.departure_picking_ids
        pickings |= self.shipment_id.arrival_picking_ids
        to_write = pickings.filtered(
            lambda r: r.state not in ('done', 'cancel'))
        to_write.write({'delivery_address_id': self.to_address_id.id})
