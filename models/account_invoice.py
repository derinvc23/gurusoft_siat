# -*- coding: utf-8 -*-
import json

from odoo import fields, models, api, _
from datetime import datetime
from pytz import timezone
import requests
# from odoo.tools.float_utils import float_round as round
import pprint
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    pago_id = fields.Many2one('siat.metodo.pago', string=u'Método Pago', copy=True)
    anulacion_id = fields.Many2one('siat.motivo.anulacion', string=u'Motivo de anulación', copy=False)
    doc_identidad_id = fields.Many2one('siat.documento.identidad', string=u'Tipo Doc. Identidad', copy=True)
    emision_id = fields.Many2one('siat.tipo.emision', string=u'Tipo Emisión', copy=True)
    tipo_fac_id = fields.Many2one('siat.tipo.factura', string=u'Tipo de Factura', copy=False)
    actividad_id = fields.Many2one('siat.actividades', related='journal_id.actividad_id', string="Actividad",
                                   store=True,
                                   readonly=True)
    doc_sector_id = fields.Many2one('siat.documento.sector', related='journal_id.doc_sector_id',
                                    string="Documento por sector", store=True,
                                    readonly=True)
    tipo_punto_venta_id = fields.Many2one('siat.tipo.punto.venta', related='journal_id.tipo_punto_venta_id',
                                          string='Tipo Punto de Venta', store=True, readonly=True)
    token_id = fields.Many2one('gurusoft.token', related='journal_id.token_id', string='Token Gurusoft', store=True)
    leyenda_id = fields.Many2one('siat.leyendas', related='journal_id.leyenda_id', string='Leyenda Factura', store=True)
    codigo_sucursal = fields.Integer(string='Codigo Sucursal', related='journal_id.codigo_sucursal', store=True,
                                     readonly=True, copy=False)
    codigo_pdv = fields.Integer(string='Codigo Punto de Venta', related='journal_id.codigo_pdv', store=True,
                                readonly=True, copy=False)
    cod_recepcion = fields.Char(string='Código de Recepción', copy=False)
    fecha_emision = fields.Char(string='Fecha Emisión', copy=False)
    fecha_anulacion = fields.Char(string='Fecha Anulación', copy=False)
    cuis = fields.Char(string='CUIS', copy=False)
    codigo_control = fields.Char(string='Código de Control', copy=False)
    cufd = fields.Char(string='CUFD', copy=False)
    url_siat = fields.Char(string='Link Factura SIAT', copy=False)
    cuf = fields.Char(string='Código Unico de Facturacion', copy=False)
    estado_siat = fields.Char(string='Estado Factura en SIAT', copy=False)
    ntarjeta = fields.Char(string='Nro Tarjeta')

    @api.multi
    def action_invoice_cancel(self):
        res = super(AccountInvoice, self).action_invoice_cancel()
        for inv in self:
            if inv.token_id:
                # inv.token_id.get_token()
                if inv.estado_siat == 'VALIDA':
                    if not inv.anulacion_id:
                        raise UserError(_("Defina Motivo de Anulación"))
                    headers = {
                        'accept': 'text/plain',
                        'Authorization': 'Bearer ' + inv.token_id.token_operaciones,
                        'Content-Type': 'application/json',
                    }

                    data = {
                        "nitEmisor": int(inv.journal_id.nit_contribuyente),
                        "codigoSucursal": inv.codigo_sucursal,
                        "codigoPuntoVenta": inv.codigo_pdv,
                        "cuf": inv.cuf,
                        "codigoMotivoAnulacion": int(inv.anulacion_id.codigo_clasificador),
                        "usuario": inv.user_id.login,
                        "nombreIntegracion": "INTEGRACION EDOC"
                    }
                    url = 'https://labbo-emp-operaciones-v2-1.guru-soft.com/api/Operaciones/AnulaDocumento'
                    if inv.token_id.op == 'prod':
                        url = 'https://bo-emp-rest-operaciones-v2-1.edocnube.com/api/Operaciones/AnulaDocumento'
                    json_invoice = json.dumps(data)
                    response = requests.post(
                        url,
                        headers=headers,
                        data=json_invoice)
                    if response.ok:
                        resp = json.loads(response.text)
                        if resp['mensajeRespuesta'] == 'ANULACION CONFIRMADA':
                            inv.write({
                                'fecha_anulacion': resp['fechaAnulacion'],
                                'estado_siat': resp['mensajeRespuesta']
                            })
                        else:
                            inv.write({
                                'estado_siat': resp['mensajeRespuesta']
                            })
                    else:
                        raise UserError(_("Error Conexion, Actualize el Token de Gurusoft"))
        return res

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        values = super(AccountInvoice, self)._prepare_refund(invoice, date_invoice, date, description, journal_id)
        if invoice.doc_identidad_id:
            values['doc_identidad_id'] = invoice.doc_identidad_id.id
        if invoice.emision_id:
            values['emision_id'] = invoice.emision_id.id
        if invoice.pago_id:
            values['pago_id'] = invoice.pago_id.id
        if invoice.tipo_fac_id:
            values['tipo_fac_id'] = invoice.tipo_fac_id.id
        return values

    @api.multi
    def action_consultar_factura(self):
        for inv in self:
            if inv.token_id:
                if inv.estado_siat == 'VALIDA':
                    if not inv.anulacion_id:
                        raise UserError(_("Defina Motivo de Anulación"))
                    headers = {
                        'accept': 'text/plain',
                        'Authorization': 'Bearer ' + inv.token_id.token_catalogo,
                        'Content-Type': 'application/json',
                    }
                    params = (
                        ('nit', inv.token_id.nit),
                        ('cuf', inv.cuf),
                    )
                    url = 'https://labbo-emp-consulta-v2-1.guru-soft.com/api/Consultar/ConsultaDocumento'
                    if inv.token_id.op == 'prod':
                        url = 'https://bo-emp-rest-consulta-v2-1.edocnube.com/api/Consultar/ConsultaDocumento'
                    response = requests.get(
                        url,
                        headers=headers, params=params)

                    if response.ok:
                        resp = json.loads(response.text)
                        inv.write({
                            'cod_recepcion': resp['codigoRecepcion'],
                            'fecha_emision': resp['fechaEmision'],
                            'cuis': resp['cuis'],
                            'codigo_control': resp['codigoControl'],
                            'cufd': resp['cufd'],
                            'url_siat': resp['linkCodigoQR'],
                            'cuf': resp['cuf'],
                            'estado_siat': resp['mensajeRespuesta']
                        })

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        for inv in self:
            curr_bob = self.env['res.currency'].search([('name', '=', 'BOB')])
            rate = curr_bob.rate
            if inv.currency_id.name == 'BOB':
                rate = 1
            now = datetime.now(timezone('America/La_Paz'))
            l10n_bo_time_sync = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
            inv_num = inv.number
            split_invoice = inv_num.split("/")
            int_inv_num = split_invoice[-1:]
            number = int(str(int_inv_num[0]))
            # Solo si esta definido con token podra emitir facturas electronicas
            if inv.token_id:
                # Actualizar token
                # inv.token_id.get_token()
                if inv.type in ('out_invoice') and not inv.type_export:
                    headers = {
                        'accept': 'text/plain',
                        'Authorization': 'Bearer ' + inv.token_id.token_factura,
                        'Content-Type': 'application/json',
                    }
                    total_descuento = round(inv.amount_discount * rate, 2)
                    # total_factura = round(inv.x_total + total_descuento, 2)
                    total_factura = 0
                    total_factura_sin = 0
                    detalles = []
                    for lines in inv.invoice_line_ids:
                        if not lines.product_id.siat_producto_id:
                            raise UserError(_("Defina Producto SIAT en el producto: %s") % (lines.product_id.name))
                        if not lines.product_id.siat_unidad_id:
                            raise UserError(
                                _("Defina Unidad de Medida SIAT en el producto: %s") % (lines.product_id.name))
                        price_unit_desc = lines.price_unit * (1 - (lines.discount or 0.0) / 100.0)
                        price_unit = round(price_unit_desc * rate, 2)

                        price_unit_sin = round(lines.price_unit * rate, 2)

                        total = round((price_unit * lines.quantity), 2)
                        total_2 = round((price_unit_sin * lines.quantity), 2)
                        total_factura += total
                        total_factura_sin += total_2
                        total_desc_a = total_2 - total
                        val_line = {
                            "ActividadEconomica": u''.join(lines.product_id.siat_producto_id.codigo_actividad).encode(
                                'utf-8'),
                            "CodigoProductoSin": u''.join(lines.product_id.siat_producto_id.codigo_producto).encode(
                                'utf-8'),
                            "CodigoProducto": u''.join(lines.product_id.default_code).encode('utf-8'),
                            "Cantidad": round(lines.quantity, 2),
                            "UnidadMedida": u''.join(lines.product_id.siat_unidad_id.codigo_clasificador).encode(
                                'utf-8'),
                            "PrecioUnitario": price_unit_sin,
                            "SubTotal": total,
                            "Descripcion": u''.join(lines.name).encode('utf-8'),
                            "MontoDescuento": round(total_desc_a, 2),
                        }
                        detalles.append(val_line)
                    total_factura = round(total_factura, 2)

                    invoice = {
                        "SecuencialERP": str(inv.id),
                        "NitEmisor": int(inv.journal_id.nit_contribuyente),
                        "RazonSocialEmisor": u''.join(inv.journal_id.razon_social).encode('utf-8'),
                        "Municipio": u''.join(inv.journal_id.nombre_unipersonal).encode('utf-8'),
                        "Telefono": u''.join(inv.company_id.phone).encode('utf-8'),
                        "NumeroDocumento": str(inv.nit),
                        "NumeroFactura": number,
                        "CodigoSucursal": inv.codigo_sucursal,
                        "Direccion": u''.join(inv.journal_id.direccion_sucursal).encode('utf-8'),
                        "CodigoPuntoVenta": inv.codigo_pdv,
                        "FechaEmision": l10n_bo_time_sync,
                        "NombreRazonSocial": u''.join(inv.partner_id.name).encode('utf-8'),
                        "CodigoTipoDocumentoIdentidad": int(inv.doc_identidad_id.codigo_clasificador),
                        "CodigoCliente": str(inv.partner_id.id),
                        "CodigoMetodoPago": int(inv.pago_id.codigo_clasificador),
                        "MontoTotal": total_factura,
                        "MontoTotalSujetoIva": total_factura,
                        "MontoTotalMoneda": total_factura,
                        "CodigoMoneda": 1,
                        "TipoCambio": 1,
                        "Leyenda": u''.join(inv.leyenda_id.descripcion).encode('utf-8'),
                        "Usuario": inv.user_id.login,
                        "TipoEmision": int(inv.emision_id.codigo_clasificador),
                        "Email": u''.join(inv.partner_id.email).encode('utf-8'),
                        "EmailResponsable": inv.token_id.email_responsable,
                        "NombreIntegracion": "INTEGRACION EDOC",
                    }

                    if inv.ntarjeta and (
                            len(inv.ntarjeta) == 16 or len(inv.ntarjeta) == 8):
                        numtarjeta_ofuscada = inv.ntarjeta[0:4] + '00000000' + inv.ntarjeta[-4:]
                        invoice.update({
                            "NumeroTarjeta": str(numtarjeta_ofuscada),
                        })
                    invoice.update({
                        "Detalles": detalles
                    })
                    url_inv = 'https://labbo-emp-emision-v2-1.guru-soft.com/api/Emitir/EmisionFacturaCompraVenta'
                    if inv.token_id.op == 'prod':
                        url_inv = 'https://bo-emp-rest-emision-v2-1.edocnube.com/api/Emitir/EmisionFacturaCompraVenta'
                    json_invoice = json.dumps(invoice)
                    pprint.pprint(json_invoice)
                    response = requests.post(
                        url_inv,
                        headers=headers,
                        data=json_invoice)
                    # print response.text
                    if response.ok:
                        resp = json.loads(response.text)
                        opcion = resp['estadoEmisionEDOC']
                        if opcion == 2:
                            if resp['mensajeRespuesta'] == 'VALIDA':
                                inv.write({
                                    'cod_recepcion': str(resp['codigoRecepcion']),
                                    'fecha_emision': str(resp['fechaEmision']),
                                    'cuis': str(resp['cuis']),
                                    'codigo_control': str(resp['codigoControl']),
                                    'cufd': str(resp['cufd']),
                                    'url_siat': str(resp['linkCodigoQR']),
                                    'cuf': str(resp['cuf']),
                                    'estado_siat': str(resp['mensajeRespuesta'])
                                })
                            else:
                                inv.write({
                                    'estado_siat': resp['mensajeRespuesta'],
                                    'fecha_emision': resp['fechaEmision'],
                                    'cuis': resp['cuis'],
                                    'codigo_control': resp['codigoControl'],
                                    'cufd': resp['cufd'],
                                    'cuf': resp['cuf'],
                                })
                        elif opcion == 8 or opcion == 5:
                            inv.write({
                                'cod_recepcion': str(resp['codigoRecepcion']),
                                'fecha_emision': str(resp['fechaEmision']),
                                'cuis': str(resp['cuis']),
                                'codigo_control': str(resp['codigoControl']),
                                'cufd': str(resp['cufd']),
                                'url_siat': str(resp['linkCodigoQR']),
                                'cuf': str(resp['cuf']),
                                'estado_siat': str(resp['mensajeRespuesta'])
                            })
                        elif resp['codigoRecepcion'] == None:
                            raise UserError(_("Error: %s") % resp['mensajeRespuesta'])

                    else:
                        raise UserError(_("Error Conexion, Actualize el Token de Gurusoft"))
                elif inv.type in ('out_refund') and inv.refund_invoice_id:
                    headers = {
                        'accept': 'text/plain',
                        'Authorization': 'Bearer ' + inv.token_id.token_factura,
                        'Content-Type': 'application/json',
                    }
                    inv_num = inv.refund_invoice_id.number
                    split_invoice = inv_num.split("/")
                    int_inv_num = split_invoice[-1:]
                    number = int(str(int_inv_num[0]))

                    total_factura_ori = 0
                    total_factura_sin_ori = 0
                    detalles = []
                    for lines in inv.refund_invoice_id.invoice_line_ids:
                        if not lines.product_id.siat_producto_id:
                            raise UserError(_("Defina Producto SIAT en el producto: %s") % (lines.product_id.name))
                        if not lines.product_id.siat_unidad_id:
                            raise UserError(
                                _("Defina Unidad de Medida SIAT en el producto: %s") % (lines.product_id.name))
                        price_unit_desc = lines.price_unit * (1 - (lines.discount or 0.0) / 100.0)
                        price_unit = round(price_unit_desc * rate, 2)

                        price_unit_sin = round(lines.price_unit * rate, 2)

                        total = round((price_unit * lines.quantity), 2)
                        total_2 = round((price_unit_sin * lines.quantity), 2)
                        total_factura_ori += total
                        total_factura_sin_ori += total_2
                        total_desc_a = total_2 - total
                        val_line = {
                            "codigoDetalleTransaccion": 1,
                            "ActividadEconomica": u''.join(lines.product_id.siat_producto_id.codigo_actividad).encode(
                                'utf-8'),
                            "CodigoProductoSin": u''.join(lines.product_id.siat_producto_id.codigo_producto).encode(
                                'utf-8'),
                            "CodigoProducto": u''.join(lines.product_id.default_code).encode('utf-8'),
                            "Cantidad": round(lines.quantity, 2),
                            "UnidadMedida": u''.join(lines.product_id.siat_unidad_id.codigo_clasificador).encode(
                                'utf-8'),
                            "PrecioUnitario": price_unit_sin,
                            "SubTotal": total,
                            "Descripcion": u''.join(lines.name).encode('utf-8'),
                            "MontoDescuento": round(total_desc_a, 2),
                        }
                        detalles.append(val_line)
                    total_factura_ori = round(total_factura_ori, 2)

                    total_factura = 0
                    total_factura_sin = 0
                    for lines in inv.invoice_line_ids:
                        if not lines.product_id.siat_producto_id:
                            raise UserError(_("Defina Producto SIAT en el producto: %s") % (lines.product_id.name))
                        if not lines.product_id.siat_unidad_id:
                            raise UserError(
                                _("Defina Unidad de Medida SIAT en el producto: %s") % (lines.product_id.name))
                        price_unit_desc = lines.price_unit * (1 - (lines.discount or 0.0) / 100.0)
                        price_unit = round(price_unit_desc * rate, 2)

                        price_unit_sin = round(lines.price_unit * rate, 2)

                        total = round((price_unit * lines.quantity), 2)
                        total_2 = round((price_unit_sin * lines.quantity), 2)
                        total_factura += total
                        total_factura_sin += total_2
                        total_desc_a = total_2 - total
                        val_line = {
                            "codigoDetalleTransaccion": 2,
                            "ActividadEconomica": u''.join(lines.product_id.siat_producto_id.codigo_actividad).encode(
                                'utf-8'),
                            "CodigoProductoSin": u''.join(lines.product_id.siat_producto_id.codigo_producto).encode(
                                'utf-8'),
                            "CodigoProducto": u''.join(lines.product_id.default_code).encode('utf-8'),
                            "Cantidad": round(lines.quantity, 2),
                            "UnidadMedida": u''.join(lines.product_id.siat_unidad_id.codigo_clasificador).encode(
                                'utf-8'),
                            "PrecioUnitario": price_unit_sin,
                            "SubTotal": total,
                            "Descripcion": u''.join(lines.name).encode('utf-8'),
                            "MontoDescuento": round(total_desc_a, 2),
                        }
                        detalles.append(val_line)

                    total_factura = round(total_factura, 2)
                    total_iva = round(total_factura * 0.13, 2)
                    str_fact = str(inv.number)[-5:]
                    c_nro = int(str_fact)
                    invoice = {
                        "SecuencialERP": str(inv.id),
                        "NitEmisor": int(inv.journal_id.nit_contribuyente),
                        "RazonSocialEmisor": u''.join(inv.journal_id.razon_social).encode('utf-8'),
                        "Municipio": u''.join(inv.journal_id.nombre_unipersonal).encode('utf-8'),
                        "Telefono": u''.join(inv.company_id.phone).encode('utf-8'),
                        "numeroNotaCreditoDebito": c_nro,
                        "NumeroFactura": number,
                        "numeroAutorizacionCUF": inv.refund_invoice_id.cuf,
                        "CodigoSucursal": inv.codigo_sucursal,
                        "Direccion": u''.join(inv.journal_id.direccion_sucursal).encode('utf-8'),
                        "CodigoPuntoVenta": inv.codigo_pdv,
                        "fechaEmision": l10n_bo_time_sync,
                        "fechaEmisionFactura": inv.refund_invoice_id.fecha_emision,
                        "montoTotalOriginal": total_factura_ori,
                        "montoTotalDevuelto": total_factura,
                        "montoDescuentoCreditoDebito": 0,
                        "montoEfectivoCreditoDebito": total_iva,
                        "NombreRazonSocial": u''.join(inv.partner_id.name).encode('utf-8'),
                        "CodigoTipoDocumentoIdentidad": int(inv.doc_identidad_id.codigo_clasificador),
                        "NumeroDocumento": str(inv.nit),
                        "CodigoCliente": str(inv.partner_id.id),
                        "Leyenda": u''.join(inv.leyenda_id.descripcion).encode('utf-8'),
                        "Usuario": inv.user_id.login,
                        "TipoEmision": int(inv.emision_id.codigo_clasificador),
                        "Email": u''.join(inv.partner_id.email).encode('utf-8'),
                        "EmailResponsable": inv.token_id.email_responsable,
                        "NombreIntegracion": "INTEGRACION EDOC",
                    }

                    if inv.ntarjeta and (
                            len(inv.ntarjeta) == 16 or len(inv.ntarjeta) == 8):
                        numtarjeta_ofuscada = inv.ntarjeta[0:4] + '00000000' + inv.ntarjeta[-4:]
                        invoice.update({
                            "NumeroTarjeta": str(numtarjeta_ofuscada),
                        })
                    invoice.update({
                        "Detalles": detalles
                    })
                    url_nota = 'https://labbo-emp-emision-v2-1.guru-soft.com/api/Emitir/EmisionNotaCreditoDebito'
                    if inv.token_id.op == 'prod':
                        url_nota = 'https://bo-emp-rest-emision-v2-1.edocnube.com/api/Emitir/EmisionNotaCreditoDebito'
                    json_invoice = json.dumps(invoice)
                    pprint.pprint(json_invoice)
                    response = requests.post(
                        url_nota,
                        headers=headers,
                        data=json_invoice)
                    # print response.text
                    if response.ok:
                        resp = json.loads(response.text)
                        if resp['mensajeRespuesta'] == 'VALIDA':
                            inv.write({
                                'cod_recepcion': resp['codigoRecepcion'],
                                'fecha_emision': resp['fechaEmision'],
                                'cuis': resp['cuis'],
                                'codigo_control': resp['codigoControl'],
                                'cufd': resp['cufd'],
                                'url_siat': resp['linkCodigoQR'],
                                'cuf': resp['cuf'],
                                'estado_siat': resp['mensajeRespuesta']
                            })
                        else:
                            inv.write({
                                'estado_siat': resp['mensajeRespuesta'],
                                'fecha_emision': resp['fechaEmision'],
                                'cuis': resp['cuis'],
                                'codigo_control': resp['codigoControl'],
                                'cufd': resp['cufd'],
                                'cuf': resp['cuf'],
                            })
                    else:
                        raise UserError(_("Error Conexion, Actualize el Token de Gurusoft"))
                if inv.type in ('out_invoice') and inv.type_export:
                    headers = {
                        'accept': 'text/plain',
                        'Authorization': 'Bearer ' + inv.token_id.token_factura,
                        'Content-Type': 'application/json',
                    }
                    total_factura = 0
                    total_factura_sin = 0
                    detalles = []
                    for lines in inv.invoice_line_ids:
                        if not lines.product_id.siat_producto_id:
                            raise UserError(_("Defina Producto SIAT en el producto: %s") % (lines.product_id.name))
                        if not lines.product_id.siat_unidad_id:
                            raise UserError(
                                _("Defina Unidad de Medida SIAT en el producto: %s") % (lines.product_id.name))
                        price_unit_desc = lines.price_unit * (1 - (lines.discount or 0.0) / 100.0)
                        price_unit = round(price_unit_desc, 2)

                        price_unit_sin = round(lines.price_unit, 2)

                        total = round((price_unit * lines.quantity), 2)
                        total_2 = round((price_unit_sin * lines.quantity), 2)
                        total_factura += total
                        total_factura_sin += total_2
                        total_desc_a = total_2 - total
                        val_line = {
                            "CodigoNandina": u''.join(lines.product_id.nandina).encode('utf-8'),
                            "ActividadEconomica": u''.join(lines.product_id.siat_producto_id.codigo_actividad).encode(
                                'utf-8'),
                            "CodigoProductoSin": u''.join(lines.product_id.siat_producto_id.codigo_producto).encode(
                                'utf-8'),
                            "CodigoProducto": u''.join(lines.product_id.default_code).encode('utf-8'),
                            "Cantidad": round(lines.quantity, 2),
                            "UnidadMedida": u''.join(lines.product_id.siat_unidad_id.codigo_clasificador).encode(
                                'utf-8'),
                            "PrecioUnitario": price_unit_sin,
                            "SubTotal": total,
                            "Descripcion": u''.join(lines.name).encode('utf-8'),
                            "MontoDescuento": 0,
                        }
                        detalles.append(val_line)

                    total_factura = round(total_factura, 2)
                    total_gas_inter = round(inv.total_gaint, 2)
                    total_gas_nacio = round(inv.total_ganac, 2)
                    monto_total_exp = round(total_factura + total_gas_inter + total_gas_nacio, 2)

                    invoice = {
                        "SecuencialERP": str(inv.id),
                        "Incoterm": str(inv.incoterms_id.code),
                        "IncotermDetalle": str(inv.incoterms_id.name),
                        "LugarDestino": str(inv.destino),
                        "PuertoDestino": str(inv.puerto),
                        "CodigoPais": inv.pais.cod_pais,
                        "NitEmisor": int(inv.journal_id.nit_contribuyente),
                        "RazonSocialEmisor": u''.join(inv.journal_id.razon_social).encode('utf-8'),
                        "Municipio": u''.join(inv.journal_id.nombre_unipersonal).encode('utf-8'),
                        "Telefono": u''.join(inv.company_id.phone).encode('utf-8'),
                        "NumeroDocumento": str(inv.nit),
                        "NumeroFactura": number,
                        "CodigoSucursal": inv.codigo_sucursal,
                        "Direccion": u''.join(inv.journal_id.direccion_sucursal).encode('utf-8'),
                        "DireccionComprador": u''.join(inv.partner_id.street).encode('utf-8'),
                        "CodigoPuntoVenta": inv.codigo_pdv,
                        "FechaEmision": l10n_bo_time_sync,
                        "NombreRazonSocial": u''.join(inv.partner_id.name).encode('utf-8'),
                        "CodigoTipoDocumentoIdentidad": int(inv.doc_identidad_id.codigo_clasificador),
                        "CodigoCliente": str(inv.partner_id.id),
                        "CodigoMetodoPago": int(inv.pago_id.codigo_clasificador),
                        "MontoDetalle": total_factura,
                        "TotalGastosNacionalesFob": total_factura + total_gas_nacio,
                        "TotalGastosInternacionales": total_gas_inter,
                        "MontoTotalMoneda": monto_total_exp,
                        "MontoTotal": round(monto_total_exp * inv.rate_export, 2),
                        "MontoTotalSujetoIva": 0,
                        "CodigoMoneda": 2,
                        "TipoCambio": inv.rate_export,
                        "Usuario": inv.user_id.login,
                        "TipoEmision": int(inv.emision_id.codigo_clasificador),
                        "Email": u''.join(inv.partner_id.email).encode('utf-8'),
                        "EmailResponsable": inv.token_id.email_responsable,
                        "NombreIntegracion": "INTEGRACION EDOC",
                    }

                    dict_nacional = {}
                    for naci in inv.gast_nac_ids:
                        dict_nacional.update({
                            str(naci.name): str(naci.amount)
                        })

                    invoice.update({
                        "costosGastosNacionales": str(dict_nacional)
                    })

                    dict_internacional = {}
                    for inte in inv.gast_int_ids:
                        dict_internacional.update({
                            str(inte.name): str(inte.amount)
                        })

                    invoice.update({
                        "costosGastosInternacionales": str(dict_internacional)
                    })

                    if inv.ntarjeta and (
                            len(inv.ntarjeta) == 16 or len(inv.ntarjeta) == 8):
                        numtarjeta_ofuscada = inv.ntarjeta[0:4] + '00000000' + inv.ntarjeta[-4:]
                        invoice.update({
                            "NumeroTarjeta": str(numtarjeta_ofuscada),
                        })
                    invoice.update({
                        "Detalles": detalles
                    })
                    url_inv = 'https://labbo-emp-emision-v2-1.guru-soft.com/api/Emitir/EmisionFacturaComercialExportacion'
                    if inv.token_id.op == 'prod':
                        url_inv = 'https://bo-emp-rest-emision-v2-1.edocnube.com/api/Emitir/EmisionFacturaComercialExportacion'
                    json_invoice = json.dumps(invoice)
                    pprint.pprint(json_invoice)
                    response = requests.post(
                        url_inv,
                        headers=headers,
                        data=json_invoice)
                    # print response.text
                    if response.ok:
                        resp = json.loads(response.text)
                        opcion = resp['estadoEmisionEDOC']
                        if opcion == 2:
                            if resp['mensajeRespuesta'] == 'VALIDA':
                                inv.write({
                                    'cod_recepcion': str(resp['codigoRecepcion']),
                                    'fecha_emision': str(resp['fechaEmision']),
                                    'cuis': str(resp['cuis']),
                                    'codigo_control': str(resp['codigoControl']),
                                    'cufd': str(resp['cufd']),
                                    'url_siat': str(resp['linkCodigoQR']),
                                    'cuf': str(resp['cuf']),
                                    'estado_siat': str(resp['mensajeRespuesta'])
                                })
                            else:
                                inv.write({
                                    'estado_siat': resp['mensajeRespuesta'],
                                    'fecha_emision': resp['fechaEmision'],
                                    'cuis': resp['cuis'],
                                    'codigo_control': resp['codigoControl'],
                                    'cufd': resp['cufd'],
                                    'cuf': resp['cuf'],
                                })
                        elif opcion == 8 or opcion == 5:
                            inv.write({
                                'cod_recepcion': str(resp['codigoRecepcion']),
                                'fecha_emision': str(resp['fechaEmision']),
                                'cuis': str(resp['cuis']),
                                'codigo_control': str(resp['codigoControl']),
                                'cufd': str(resp['cufd']),
                                'url_siat': str(resp['linkCodigoQR']),
                                'cuf': str(resp['cuf']),
                                'estado_siat': str(resp['mensajeRespuesta'])
                            })
                        elif resp['codigoRecepcion'] == None:
                            raise UserError(_("Error: %s") % resp['mensajeRespuesta'])

                    else:
                        raise UserError(_("Error Conexion, Actualize el Token de Gurusoft"))
            return res
