# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class SiatActividades(models.Model):
    _description = 'Siat Activities'
    _name = 'siat.actividades'
    _rec_name = 'descripcion'
    codigo_caeb = fields.Char(u'Código Caeb')
    descripcion = fields.Char(u'Descripcion')
    tipo_actividad = fields.Selection([
        ('S', 'S'),
        ('P', 'P')
    ], string='Tipo Actividad')


class SiatMensajes(models.Model):
    _name = 'siat.mensajes'
    _description = 'Mensajes SIAT'
    _rec_name = 'descripcion'
    descripcion = fields.Char('Mensaje del servicio')
    codigo_clasificador = fields.Char(u'Código Clasificador')


class SiatEventos(models.Model):
    _name = 'siat.eventos'
    _description = 'Eventos Facturas'
    _rec_name = 'descripcion'

    descripcion = fields.Char('Mensaje del servicio')
    codigo_clasificador = fields.Char(u'Código Clasificador')


class SiatMotivoAnulacion(models.Model):
    _name = 'siat.motivo.anulacion'
    _description = u'Motivo Anulación'
    _rec_name = 'descripcion'

    descripcion = fields.Char(u'Motivo Anulación')
    codigo_clasificador = fields.Char(u'Código Clasificador')


class SiatPaises(models.Model):
    _name = 'siat.paises'
    _description = 'Paises de Origen'
    _rec_name = 'descripcion'

    descripcion = fields.Char('Pais de Origen')
    codigo_clasificador = fields.Char(u'Código Clasificador')


class SiatDocumentoIdentidad(models.Model):
    _name = 'siat.documento.identidad'
    _description = 'Tipos de Documento Identidad'
    _rec_name = 'descripcion'

    descripcion = fields.Char(u'Documento Identidad')
    codigo_clasificador = fields.Char(u'Código Clasificador')


class SiatDocumentoSector(models.Model):
    _name = 'siat.documento.sector'
    _description = 'Documentos por Sector'
    _rec_name = 'descripcion'

    descripcion = fields.Char(u'Tipo Documento Sector')
    codigo_clasificador = fields.Char(u'Código Clasificador')
    codigo_sector = fields.Char(u'Código Sector')


class SiatTipoEmision(models.Model):
    _name = 'siat.tipo.emision'
    _description = u'Tipo de Emisión'
    _rec_name = 'descripcion'

    descripcion = fields.Char(u'Tipo de Emisión')
    codigo_clasificador = fields.Char(u'Código Clasificador')


class SiatMetodoPago(models.Model):
    _name = 'siat.metodo.pago'
    _description = u'Tipos Métodos Pago'
    _rec_name = 'descripcion'

    descripcion = fields.Char(u'Método de Pago')
    codigo_clasificador = fields.Char(u'Código Clasificador')


class SiatTipoMoneda(models.Model):
    _name = 'siat.tipo.moneda'
    _description = 'Tipo de Moneda'
    _rec_name = 'descripcion'

    descripcion = fields.Char(u'Moneda')
    codigo_clasificador = fields.Char(u'Código Clasificador')


class SiatTipoPuntoVenta(models.Model):
    _name = 'siat.tipo.punto.venta'
    _description = 'Tipo Punto Venta'
    _rec_name = 'descripcion'

    descripcion = fields.Char(u'Tipo Punto de Venta')
    codigo_clasificador = fields.Char(u'Código Clasificador')


class SiatTipoFactura(models.Model):
    _name = 'siat.tipo.factura'
    _description = 'Tipo Factura'
    _rec_name = 'descripcion'

    descripcion = fields.Char(u'Tipo Factura')
    codigo_clasificador = fields.Char(u'Código Clasificador')


class SiatUnidadMedida(models.Model):
    _name = 'siat.unidad.medida'
    _description = 'Unidad Medida'
    _rec_name = 'descripcion'

    descripcion = fields.Char(u'Unidad Medida')
    codigo_clasificador = fields.Char(u'Código Clasificador')


class SiatProductos(models.Model):
    _name = 'siat.productos'
    _description = 'Productos Siat'
    _rec_name = 'descripcion_producto'

    descripcion_producto = fields.Char(u'Producto')
    codigo_producto = fields.Char(u'Código Producto')
    codigo_actividad = fields.Char(u'Código Actividad')


class SiatLeyendas(models.Model):
    _name = 'siat.leyendas'
    _description = 'Leyendas Facturas'
    _rec_name = 'descripcion'

    descripcion = fields.Char(u'Leyenda')
    actividad = fields.Char(u'Actividad Económica')
    codigo_leyenda = fields.Char(u'Código Actividad Económicar')
