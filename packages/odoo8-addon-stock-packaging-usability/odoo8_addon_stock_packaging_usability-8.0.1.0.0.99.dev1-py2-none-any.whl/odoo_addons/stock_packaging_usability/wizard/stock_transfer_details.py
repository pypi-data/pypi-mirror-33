# -*- encoding: utf-8 -*-
##############################################################################
#
#    Stock Packaging Usability module for Odoo
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
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

from openerp import models, api, _
from openerp.exceptions import Warning


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.multi
    def put_residual_in_new_pack(self):
        for wiz in self:
            items_to_update = wiz.item_ids
            for item in wiz.item_ids:
                if item.result_package_id:
                    items_to_update -= item
                if not item.quantity:
                    items_to_update -= item
            items_to_update.put_in_pack()
        if self and self[0]:
            return self[0].wizard_view()


class StockTransferDetailsItems(models.TransientModel):
    _inherit = 'stock.transfer_details_items'

    @api.multi
    def put_in_last_pack(self):
        for packop in self:
            if packop.result_package_id:
                raise Warning(
                    _('This product is already in a package !'))
            all_cur_packs_ids = [
                packop2.result_package_id.id for packop2
                in self.transfer_id.item_ids if packop2.result_package_id]
            if not all_cur_packs_ids:
                raise Warning(
                    _('There is no current package'))
            all_cur_packs_ids.sort()
            packop.result_package_id = all_cur_packs_ids[-1]
        if self and self[0]:
            return self[0].transfer_id.wizard_view()
