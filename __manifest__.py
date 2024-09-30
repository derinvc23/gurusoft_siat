# -*- coding: utf-8 -*-
{
    'name': 'Facturacion Electronica GURUSOFT',
    'version': '10.0.0.1',
    'sequence': 14,
    'summary': 'Facturación Gurusoft',
    'license': 'AGPL-3',
    'description': """
    Integración Gurusoft - Odoo
    """,
    'category': 'Accounting',
    'website': 'https://jadetpa.com',
    'depends': ['base', 'account', 'invoice_bo', 'invoice_export'],
    'data': [
        'views/product_product_view.xml',
        'views/product_template_view.xml',
        'views/siat_catalogo_view.xml',
        'views/gurusoft_token_view.xml',
        'views/account_journal_view.xml',
        'views/account_invoice_view.xml',
        'views/gurusoft_token_view.xml',
        'views/currency_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
