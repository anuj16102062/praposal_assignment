from odoo import http
from odoo.http import request

class ProposalController(http.Controller):

    @http.route(['/proposal/<int:proposal_id>'], type='http', auth='public', website=True)
    def view_proposal(self, proposal_id, token=None, **kwargs):
        proposal = request.env['business.proposal'].sudo().browse(proposal_id)
        if proposal and proposal.external_link.endswith(token):
            return request.render('praposal.proposal_page', {
                'proposal': proposal,
                'lines': proposal.proposal_line_ids,
            })
        return request.render('website.404')

    @http.route(['/proposal/accept'], type='json', auth='public', website=True)
    def accept_proposal(self, proposal_id, token, lines, **kwargs):
        proposal = request.env['business.proposal'].sudo().browse(proposal_id)
        if proposal.state not in ['sent','draft']:
            return {'status': 'success','data':'You have already submitted your response.'}
        if proposal and proposal.external_link.endswith(token):
            for line in lines:
                line_id = int(line['id'])
                qty_accepted = float(line['qty_accepted'])
                price_accepted = float(line['price_accepted'])
                proposal_line = proposal.proposal_line_ids.filtered(lambda l: l.id == line_id)
                proposal_line.write({
                    'qty_accepted': qty_accepted,
                    'price_accepted': price_accepted,
                })
            proposal.state = 'accept'
            return {'status': 'success','data':'Thanks for accepting my proposal.'}
        return {'status': 'error'}

    @http.route(['/proposal/refuse'], type='json', auth='public', website=True)
    def refuse_proposal(self, proposal_id, token, **kwargs):
        proposal = request.env['business.proposal'].sudo().browse(proposal_id)
        if proposal.state not in ['sent','draft']:
            return {'status': 'success','data':'You have already submitted your response.'}
        if proposal and proposal.external_link.endswith(token):
            proposal.state = 'cancel'
            return {'status': 'success','data':'Your request has been saved.'}
        return {'status': 'error'}
