from odoo import models, fields, api, _


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    moneda_siat_id = fields.Many2one('siat.tipo.moneda', string='Moneda SIAT')
