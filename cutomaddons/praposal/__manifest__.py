{
    'name': 'Business Proposal',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Manage Business Proposals',
    'depends': ['sale', 'mail', 'website','website_payment'],
    'data': [
        'security/ir.model.access.csv',
        'data/praposal_mail_template.xml',
        'views/praposal_views.xml',
        'data/sequence.xml',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'praposal/static/src/js/praposal_action.js',
        ],
    },
}
