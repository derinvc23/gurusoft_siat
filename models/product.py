# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    siat_unidad_id = fields.Many2one('siat.unidad.medida', string='Unidad Medida SIN')
    siat_producto_id = fields.Many2one('siat.productos', string=u'Código Producto SIN')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.depends('product_variant_ids', 'product_variant_ids.siat_unidad_id')
    def _compute_unidad(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.siat_unidad_id = template.product_variant_ids.siat_unidad_id.id
        for template in (self - unique_variants):
            template.siat_unidad_id = False

    @api.one
    def _set_unidad(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.siat_unidad_id = self.siat_unidad_id.id

    @api.depends('product_variant_ids', 'product_variant_ids.siat_producto_id')
    def _compute_producto(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.siat_producto_id = template.product_variant_ids.siat_producto_id.id
        for template in (self - unique_variants):
            template.siat_producto_id = False

    @api.one
    def _set_producto(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.siat_producto_id = self.siat_producto_id.id

    siat_unidad_id = fields.Many2one('siat.unidad.medida', string='Unidad Medida SIN', compute='_compute_unidad',
                                     inverse='_set_unidad', store=True)
    siat_producto_id = fields.Many2one('siat.productos', string=u'Código Producto SIN', compute='_compute_producto',
                                       inverse='_set_producto', store=True)
