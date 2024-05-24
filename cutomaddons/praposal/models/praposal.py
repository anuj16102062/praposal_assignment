from odoo import api, fields, models, _
import uuid
class Proposal(models.Model):
    _name = 'business.proposal'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Business Proposal'
    _order = 'name desc'

    name = fields.Char(string='Proposal Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    salesman_id = fields.Many2one('res.users', string='Salesperson', required=True, index=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, index=True, tracking=True)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=True)
    proposal_line_ids = fields.One2many('business.proposal.line', 'proposal_id', string='Proposal Lines', copy=True, auto_join=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accept', 'Accepted'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='draft')
    amount_total_proposed = fields.Float(string='Total Proposed', compute='_compute_amount', store=True)
    amount_total_accepted = fields.Float(string='Total Accepted', compute='_compute_amount', store=True)
    external_link = fields.Char(string='External Link', readonly=True)
    message_ids = fields.One2many('mail.message', 'res_id', domain=lambda self: [('model', '=', self._name)], string='Messages')
    message_follower_ids = fields.One2many('mail.followers', 'res_id', domain=lambda self: [('res_model', '=', self._name)], string='Followers')


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('business.proposal') or _('New')
        proposal = super(Proposal, self).create(vals)
        proposal.external_link = proposal._generate_external_link()
        return proposal

    def _generate_external_link(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f"{base_url}/proposal/{self.id}?token={self._generate_token()}"

    def _generate_token(self):
        return str(uuid.uuid4())

    @api.depends('proposal_line_ids.price_proposed', 'proposal_line_ids.price_accepted')
    def _compute_amount(self):
        for proposal in self:
            total_proposed = total_accepted = 0.0
            for line in proposal.proposal_line_ids:
                total_proposed += line.price_proposed * line.qty_proposed
                total_accepted += line.price_accepted * line.qty_accepted
            proposal.update({
                'amount_total_proposed': total_proposed,
                'amount_total_accepted': total_accepted,
            })

    def action_send(self):
        template_id = self.env.ref('praposal.email_template_for_proposal').id
        self.env['mail.template'].browse(template_id).send_mail(self.id, force_send=True)
        self.state = 'sent'

    def action_confirm(self):
        self.state = 'confirmed'
        self._create_sales_order()

    def action_cancel(self):
        self.state = 'cancel'

    def _create_sales_order(self):
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'pricelist_id': self.pricelist_id.id,
            'order_line': [(0, 0, {
                'product_id': line.product_id.id,
                'name': line.label,
                'product_uom_qty': line.qty_accepted,
                'price_unit': line.price_accepted,
            }) for line in self.proposal_line_ids]
        })
        sale_order.action_confirm()
