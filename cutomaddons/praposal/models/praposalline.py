from odoo import api, fields, models, _
class ProposalLine(models.Model):
    _name = 'business.proposal.line'
    _description = 'Proposal Line'

    proposal_id = fields.Many2one('business.proposal', string='Proposal Reference', required=True, ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    label = fields.Char(string='Description')
    qty_proposed = fields.Float(string='Quantity Proposed', required=True, default=1.0)
    qty_accepted = fields.Float(string='Quantity Accepted', default=0.0)
    price_proposed = fields.Float(string='Price Proposed', required=True)
    price_accepted = fields.Float(string='Price Accepted')

    @api.onchange('product_id', 'qty_proposed', 'proposal_id.pricelist_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.label = self.product_id.name
            self.price_proposed = self.product_id.with_context(pricelist=self.proposal_id.pricelist_id.id).price
            self.price_accepted = self.price_proposed
            self.qty_accepted = self.qty_proposed
