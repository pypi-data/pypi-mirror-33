# -*- coding: utf-8 -*-
# © 2015 Vauxoo
# © 2009-2012  Akretion
# Author: Emmanuel Samyn, Benoît GUILLOT <benoit.guillot@akretion.com>,
#         Osval Reyes
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ClaimMakePicking(models.TransientModel):

    _inherit = 'claim_make_picking.wizard'
    _description = 'Wizard to create pickings from claim lines'

    def _default_claim_line_dest_location_id(self):
        """Return the location_id to use as destination.

        If it's an outgoing shipment: take the customer stock property
        If it's an incoming shipment take the location_dest_id common to all
        lines, or if different, return None.
        """
        picking_type = self.env.context.get('picking_type')
        claim_id = self.env.context.get('active_id')
        claim_record = self.env['crm.claim'].browse(claim_id)

        if isinstance(picking_type, int):
            picking_obj = self.env['stock.picking.type']
            return picking_obj.browse(picking_type)\
                .default_location_dest_id

        if picking_type == 'out':
            return claim_record.warehouse_id.rma_out_type_id.\
                default_location_dest_id
        elif picking_type == 'in':
            return claim_record.warehouse_id.rma_in_type_id.\
                default_location_dest_id
        elif picking_type == 'int':
            return claim_record.warehouse_id.rma_int_type_id.\
                default_location_dest_id
        elif picking_type == 'loss':
            return claim_record.warehouse_id.loss_loc_id

        return self.env['stock.location']

    claim_line_dest_location_id = fields.Many2one(
        default=_default_claim_line_dest_location_id)
