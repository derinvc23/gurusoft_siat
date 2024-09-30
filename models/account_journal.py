# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountJournal(models.Model):
    _inherit = "account.journal"

    actividad_id = fields.Many2one('siat.actividades', string=u'Actividades')
    doc_sector_id = fields.Many2one('siat.documento.sector', string=u'Documentos por sector')
    tipo_punto_venta_id = fields.Many2one('siat.tipo.punto.venta', string='Tipo Punto de Venta')
    codigo_sucursal = fields.Integer(string='Codigo Sucursal')
    codigo_pdv = fields.Integer(string='Codigo Punto de Venta')
    token_id = fields.Many2one('gurusoft.token', string='Token Gurusoft')
    leyenda_id = fields.Many2one('siat.leyendas', string='Leyenda')
