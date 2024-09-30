# -*- coding: utf-8 -*-
import base64
import json
import requests
from odoo import fields, models


class GurusoftToken(models.Model):
    _name = "gurusoft.token"

    name = fields.Char('Token')
    nit = fields.Char('NIT')
    user = fields.Char('Usuario Key')
    password = fields.Char('Password')
    email_responsable = fields.Char(string='E-mail Responsable seguimiento')
    token_factura = fields.Text('Token Facturas')
    token_catalogo = fields.Text('Token Catalogos')
    token_operaciones = fields.Text('Token Operaciones')
    expedido = fields.Datetime('Fecha Expedido')
    expira = fields.Datetime('Fecha Vencimiento')
    active = fields.Boolean('Activos', default=True)
    op = fields.Selection([('labo', 'Pruebas'),
                           ('prod', 'Producción')], default='labo', string='Modo Facturación')
    company_id = fields.Many2one('res.company', string=u'Compañía',
                                 default=lambda self: self.env.user.company_id)

    def get_token(self):
        usrPass = self.user + ':' + self.password
        b64Val = base64.b64encode(usrPass)
        url = "https://labbo-emp-auth-v2-1.guru-soft.com/ServicioEDOC/"
        if self.op == 'prod':
            url = "https://bo-emp-rest-auth-v2-1.edocnube.com/ServicioEDOC/"
        r = requests.get(url + "?id=1",
                         headers={"Authorization": "Basic %s" % b64Val},
                         data=[])
        data = json.loads(r.content)
        self.token_factura = str(data['token'])

        r2 = requests.get(url + "?id=3",
                          headers={"Authorization": "Basic %s" % b64Val},
                          data=[])

        data2 = json.loads(r2.content)
        self.token_catalogo = str(data2['token'])

        r3 = requests.get(url + "?id=5",
                          headers={"Authorization": "Basic %s" % b64Val},
                          data=[])
        data3 = json.loads(r3.content)
        self.token_operaciones = str(data3['token'])

    def sincronizar_catalogo(self):
        # Catalogos
        headers = {
            'accept': 'text/plain',
            'Authorization': 'Bearer ' + self.token_catalogo,
        }
        url = "https://labbo-emp-consulta-v2-1.guru-soft.com/api/Consultar/ConsultarCatalogoGeneral"
        if self.op == 'prod':
            url = "https://bo-emp-rest-consulta-v2-1.edocnube.com/api/Consultar/ConsultarCatalogoGeneral"

        # Actividades
        params = (
            ('nit', self.nit),
            ('catalogo', '1'),
        )
        response = requests.get(url,
                                headers=headers, params=params)
        actividades = self.env['siat.actividades']
        data = json.loads(response.content)
        for line in data:
            dato = actividades.search([('codigo_caeb', '=', line['codigo'])])
            if not dato:
                new_record = {
                    'codigo_caeb': line['codigo'],
                    'descripcion': line['descripcion'],
                }
                actividades.create(new_record)

        # Mensajes
        params = (
            ('nit', self.nit),
            ('catalogo', '3'),
        )
        response = requests.get(
            url,
            headers=headers, params=params)
        mensajes = self.env['siat.mensajes']
        data = json.loads(response.content)
        for line in data:
            dato = mensajes.search([('codigo_clasificador', '=', line['codigo'])])
            if not dato:
                new_record = {
                    'codigo_clasificador': line['codigo'],
                    'descripcion': line['descripcion'],
                }
                mensajes.create(new_record)

        # Eventos
        params = (
            ('nit', self.nit),
            ('catalogo', '5'),
        )
        response = requests.get(
            url,
            headers=headers, params=params)
        eventos = self.env['siat.eventos']
        data = json.loads(response.content)
        for line in data:
            dato = eventos.search([('codigo_clasificador', '=', line['codigo'])])
            if not dato:
                new_record = {
                    'codigo_clasificador': line['codigo'],
                    'descripcion': line['descripcion'],
                }
                eventos.create(new_record)

        # Motivos Anulacion
        params = (
            ('nit', self.nit),
            ('catalogo', '6'),
        )
        response = requests.get(
            url,
            headers=headers, params=params)
        motivos = self.env['siat.motivo.anulacion']
        data = json.loads(response.content)
        for line in data:
            dato = motivos.search([('codigo_clasificador', '=', line['codigo'])])
            if not dato:
                new_record = {
                    'codigo_clasificador': line['codigo'],
                    'descripcion': line['descripcion'],
                }
                motivos.create(new_record)

        # Paises
        params = (
            ('nit', self.nit),
            ('catalogo', '7'),
        )
        response = requests.get(
            url,
            headers=headers, params=params)
        paises = self.env['siat.paises']
        data = json.loads(response.content)
        for line in data:
            dato = paises.search([('codigo_clasificador', '=', line['codigo'])])
            if not dato:
                new_record = {
                    'codigo_clasificador': line['codigo'],
                    'descripcion': line['descripcion'],
                }
                paises.create(new_record)

        # Tipos decumento identidad
        params = (
            ('nit', self.nit),
            ('catalogo', '8'),
        )
        response = requests.get(
            url,
            headers=headers, params=params)
        tipos_documento = self.env['siat.documento.identidad']
        data = json.loads(response.content)
        for line in data:
            dato = tipos_documento.search([('codigo_clasificador', '=', line['codigo'])])
            if not dato:
                new_record = {
                    'codigo_clasificador': line['codigo'],
                    'descripcion': line['descripcion'],
                }
                tipos_documento.create(new_record)

        # Documentos por sector
        params = (
            ('nit', self.nit),
            ('catalogo', '9'),
        )
        response = requests.get(
            url,
            headers=headers, params=params)
        documento_sector = self.env['siat.documento.sector']
        data = json.loads(response.content)
        for line in data:
            dato = documento_sector.search([('codigo_clasificador', '=', line['codigo'])])
            if not dato:
                new_record = {
                    'codigo_clasificador': line['codigo'],
                    'descripcion': line['descripcion'],
                }
                documento_sector.create(new_record)

        # Tipo Emisión
        params = (
            ('nit', self.nit),
            ('catalogo', '10'),
        )
        response = requests.get(
            url,
            headers=headers, params=params)
        tipo_emision = self.env['siat.tipo.emision']
        data = json.loads(response.content)
        for line in data:
            dato = tipo_emision.search([('codigo_clasificador', '=', line['codigo'])])
            if not dato:
                new_record = {
                    'codigo_clasificador': line['codigo'],
                    'descripcion': line['descripcion'],
                }
                tipo_emision.create(new_record)

        # Metodo Pago
        params = (
            ('nit', self.nit),
            ('catalogo', '11'),
        )
        response = requests.get(
            url,
            headers=headers, params=params)
        metodo_pago = self.env['siat.metodo.pago']
        data = json.loads(response.content)
        for line in data:
            dato = metodo_pago.search([('codigo_clasificador', '=', line['codigo'])])
            if not dato:
                new_record = {
                    'codigo_clasificador': line['codigo'],
                    'descripcion': line['descripcion'],
                }
                metodo_pago.create(new_record)

        # Tipo Moneda
        params = (
            ('nit', self.nit),
            ('catalogo', '12'),
        )
        response = requests.get(
            url,
            headers=headers, params=params)
        tipo_moneda = self.env['siat.tipo.moneda']
        data = json.loads(response.content)
        for line in data:
            dato = tipo_moneda.search([('codigo_clasificador', '=', line['codigo'])])
            if not dato:
                new_record = {
                    'codigo_clasificador': line['codigo'],
                    'descripcion': line['descripcion'],
                }
                tipo_moneda.create(new_record)

        # Tipo Punto de Venta
        params = (
            ('nit', self.nit),
            ('catalogo', '13'),
        )
        response = requests.get(
            url,
            headers=headers, params=params)
        tipo_punto = self.env['siat.tipo.punto.venta']
        data = json.loads(response.content)
        for line in data:
            dato = tipo_punto.search([('codigo_clasificador', '=', line['codigo'])])
            if not dato:
                new_record = {
                    'codigo_clasificador': line['codigo'],
                    'descripcion': line['descripcion'],
                }
                tipo_punto.create(new_record)

        # Tipo Factura
        params = (
            ('nit', self.nit),
            ('catalogo', '14'),
        )
        response = requests.get(
            url,
            headers=headers, params=params)
        tipo_factura = self.env['siat.tipo.factura']
        data = json.loads(response.content)
        for line in data:
            dato = tipo_factura.search([('codigo_clasificador', '=', line['codigo'])])
            if not dato:
                new_record = {
                    'codigo_clasificador': line['codigo'],
                    'descripcion': line['descripcion'],
                }
                tipo_factura.create(new_record)

        # Unidad de medida
        params = (
            ('nit', self.nit),
            ('catalogo', '15'),
        )
        response = requests.get(
            url,
            headers=headers, params=params)
        unidad_medida = self.env['siat.unidad.medida']
        data = json.loads(response.content)
        for line in data:
            dato = unidad_medida.search([('codigo_clasificador', '=', line['codigo'])])
            if not dato:
                new_record = {
                    'codigo_clasificador': line['codigo'],
                    'descripcion': line['descripcion'],
                }
                unidad_medida.create(new_record)
