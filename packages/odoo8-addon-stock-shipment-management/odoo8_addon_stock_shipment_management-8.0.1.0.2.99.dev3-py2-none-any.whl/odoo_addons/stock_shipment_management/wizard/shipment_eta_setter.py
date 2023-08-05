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
from openerp import models, fields, api, exceptions, _


class ETASetter(models.TransientModel):
    _name = "shipment.eta.setter"
    _inherit = "shipment.value.setter"

    eta = fields.Datetime(
        'ETA',
        help="Up to date Estimated Time of Arrival"
    )

    @api.multi
    def set_value(self):
        """ Changes the Shipment ETA and update arrival moves """
        etd = self.shipment_id.etd
        if etd and etd > self.eta:
            raise exceptions.Warning(_("ETA must be after ETD (%s)" % etd))
        self.shipment_id.eta = self.eta
        moves = self.shipment_id.arrival_move_ids
        to_write = moves.filtered(lambda r: r.state not in ('done', 'cancel'))
        to_write.write({'date_expected': self.eta})
