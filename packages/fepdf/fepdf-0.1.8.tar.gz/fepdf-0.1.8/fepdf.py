# -*- coding: utf-8 -*-
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3, or (at your option) any later
# version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTIBILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
fepdf: Modulo para generar PDF de facturas electrónicas

Importante: Este modulo no autoriza facturas de AFIP. Antes de emitir un\
PDF de una factura debe estar propiamente autorizada por AFIP, obeniendo\
el CAE, su vencimiento, etc. Aqui, siempre se supone este paso realizado.

Para generar el pdf, el modulo se vale de una plantilla que tiene etiquetas
que indicar que se debe imprimir y donde. Es un archivo CSV, donde cada linea
esta dividida por ';', formando 16 campos. Vea el archivo de ejemplo para
conocer mas del formato pero tienen el siguiente significado

* nombre
* tipo
* x1
* y1
* x2
* y2
* font
* size
* bold
* italic
* underline
* foreground
* background
* align
* text
* priority

Para generar PDF debe utilizar la Clase FEPDF, el primer paso, como siempre,
es instanciar la clase. Toma atributos que definen como se emitira el PDF
(como el tamaño de hoja, la orientacion, etc.).

Luego, hay que cargar la plantilla con cargar_formato. En este momento ya se ha
creado el objeto template, por lo que se puede agregar nuevas fuentes usado
obj.template.pdf.add_font(). A continuacion hay que enviarle la informacion de
la factura con el metodo crear_factura. Tiene muchos atributos, vea su
referencia para conocer el significado decada uno.


Si ha modificado la plantilla y agregado etiquetas, debe llamar
a agregar_dato para darle un valor.

A continuacion, multiple llamadas a agregar_item, para agregar el detalle
de la factura.

Si es una NDC o NDC, puede agregarle un comprobante relacionado con
agregar_cmp_asoc

Si es factura A, debe llamar a agregar_iva por cada alicuota iva que haya en
su detalle.

Si corresponde otros tributos, como percepciones, los debe agregar con
agregar_tributo

Para finalizar debe llamar a procesar_plantilla que es donde se realiza el
verdero trabajo. Por ultimo, llame a render e indique un path donde se
guardar el archivo en PDF.

```
obj = FEPDF()
obj.cargar_formato(path_to_factura_csv)
# obj.template.pdf.add_font()
obj.crear_factura()
obj.agregar_dato()
obj.procesar_plantilla()
obj.render()
```


"""

import datetime
import locale
import math
import os
from collections import defaultdict
from decimal import Decimal

from fpdf import Template

#
# Constants
#
VERSION = "0.1.8"
FMTCANTIDAD = "0.2"
FMTPRECIO = "0.2"
PAPER_SIZE = ["A4", "A5", "letter", "legal"]
COPIAS = {1: 'Original', 2: 'Duplicado', 3: 'Triplicado'}
MSGS = {
    "no_iva": "\nEl IVA discriminado no puede computarse como Crédito Fiscal "
    "(RG2485/08 Art. 30 inc. c).",
    "tmpl_nber_values": "Formato Incorrecto. cada fila debe tener 16 campos"
}
DOCS = {
    80: 'CUIT', 86: 'CUIL', 96: 'DNI', 99: '', 87: "CDI",
    89: "LE", 90: "LC", 91: "CI Extranjera",
    92: "en trámite", 93: "Acta Nacimiento", 94: "Pasaporte",
    95: "CI Bs. As. RNP",
    0: "CI Policía Federal", 1: "CI Buenos Aires",
    2: "CI Catamarca", 3: "CI Córdoba", 4: "CI Corrientes",
    5: "CI Entre Ríos", 6: "CI Jujuy", 7: "CI Mendoza",
    8: "CI La Rioja", 9: "CI Salta", 10: "CI San Juan",
    11: "CI San Luis", 12: "CI Santa Fe",
    13: "CI Santiago del Estero", 14: "CI Tucumán",
    16: "CI Chaco", 17: "CI Chubut", 18: "CI Formosa",
    19: "CI Misiones", 20: "CI Neuquén", 21: "CI La Pampa",
    22: "CI Río Negro", 23: "CI Santa Cruz",
    24: "CI Tierra del Fuego",
}
IVAS_DS = {
    3: 0,
    4: 10.5,
    5: 21,
    6: 27,
    8: 5,
    9: 2.5
}
UMEDS_DS = {
    0: '', 1: 'kg', 2: 'm', 3: 'm2', 4: 'm3', 5: 'l',
    6: '1000 kWh', 7: 'u',
    8: 'pares', 9: 'docenas', 10: 'quilates', 11: 'millares',
    14: 'g', 15: 'mm', 16: 'mm3', 17: 'km', 18: 'hl', 20: 'cm',
    25: 'jgo. pqt. mazo naipes', 27: 'cm3', 29: 'tn',
    30: 'dam3', 31: 'hm3', 32: 'km3', 33: 'ug', 34: 'ng', 35: 'pg',
    41: 'mg', 47: 'mm',
    48: 'curie', 49: 'milicurie', 50: 'microcurie', 51: 'uiacthor',
    52: 'muiacthor',
    53: 'kg base', 54: 'gruesa', 61: 'kg bruto',
    62: 'uiactant', 63: 'muiactant', 64: 'uiactig', 65: 'muiactig',
    66: 'kg activo',
    67: 'gramo activo', 68: 'gramo base', 96: 'packs', 97: 'hormas',
    96: 'packs', 97: 'seña/anticipo',
    99: 'bonificación', 98: 'otras unidades'
}

TRIBUTOS_DS = {
    1: 'Impuestos nacionales',
    2: 'Impuestos provinciales',
    3: 'Impuestos municipales',
    4: 'Impuestos Internos',
    99: 'Otro'
}
TIPOS_FACT = {
    (1, 6, 11, 19, 51): 'Factura',
    (2, 7, 12, 20, 52): 'Nota de Débito',
    (3, 8, 13, 21, 53): 'Nota de Crédito',
    (4, 9, 15, 54): 'Recibo',
    (10, 5): 'Nota de Venta al contado',
    (60, 61): 'Cuenta de Venta y Líquido producto',
    (63, 64): 'Liquidación',
    (91, ): 'Remito',
    (39, 40): '???? (R.G. Nº 3419)'
}
LETRAS_FACT = {
    (1, 2, 3, 4, 5, 39, 60, 63): 'A',
    (6, 7, 8, 9, 10, 40, 61, 64): 'B',
    (11, 12, 13, 15): 'C',
    (51, 52, 53, 54): 'M',
    (19, 20, 21): 'E',
    (91, ): 'R',
}


#
# funciones de formateo de strings:
#
def fmt_date(d):
    """Formatear una fecha.
    :param (date) d: la fecha a formatear
    """

    if not d:
        return ''
    return d.strftime("%d/%m/%Y")


def fmt_num(i, fmt=None, monetary=True):
    if i in (None, ''):
        return ''
    if not fmt:
        fmt = "%" + FMTPRECIO + "f"

    return locale.format(fmt, Decimal(i),
                         grouping=True,
                         monetary=monetary)


def fmt_qty(i):
    return fmt_num(i, "%" + FMTCANTIDAD + "f", False)


def fmt_cuit(c):
    c = str(c)
    return "{}-{:08}-{}".format(c[0:2], int(c[2:-1]), c[-1])


def fmt_iva(i):
    """Formatea el codigo de alicuota iva. Ej: 4 => 10.5%"""
    if not i:
        return ''

    p = IVAS_DS[i]
    if p == int(p):
        return fmt_num(p, "%d") + "%"
    else:
        return fmt_num(p, "%.1f") + "%"


def fmt_fact(tipo_cbte, punto_vta, cbte_nro):
    """Formatea tipo, letra, punto de venta y número de factura"""

    n = "{:04}-{:08}".format(punto_vta, cbte_nro)
    t = None
    l = None

    for k, v in TIPOS_FACT.items():
        if tipo_cbte in k:
            t = v
    for k, v in LETRAS_FACT.items():
        if tipo_cbte in k:
            l = v

    return t, l, n


def humanize_bytes(bytes):
    units = [' kB', ' MB', ' GB', ' TB', 'PB', 'EB', 'ZB', 'YB']
    i = -1

    while bytes > 1024:
        bytes /= 1024
        i += 1

    return "{}{}".format(int(bytes * 100) / 100, units[i])


def digito_verificador_modulo10(codigo):
    """Rutina para el cálculo del dígito verificador 'módulo 10'"""
    # http://www.consejo.org.ar/Bib_elect/diciembre04_CT/documentos/rafip1702.htm
    # Etapa 1: comenzar desde la izquierda, sumar todos los caracteres
    # ubicados en las posiciones impares.
    codigo = codigo.strip()
    if not codigo or not codigo.isdigit():
        return ''
    etapa1 = sum([int(c) for i, c in enumerate(codigo) if not i % 2])
    # Etapa 2: multiplicar la suma obtenida en la etapa 1 por el numero 3
    etapa2 = etapa1 * 3
    # Etapa 3: comenzar desde la izquierda, sumar todos los caracteres que
    # estan ubicados en las posiciones pares.
    etapa3 = sum([int(c) for i, c in enumerate(codigo) if i % 2])
    # Etapa 4: sumar los resultados obtenidos en las etapas 2 y 3.
    etapa4 = etapa2 + etapa3
    # Etapa 5: buscar el menor numero que sumado al resultado obtenido
    # en la etapa 4 de un numero multiplo de 10. Este sera el valor del
    # digito verificador del modulo 10.
    digito = 10 - (etapa4 - (int(etapa4 / 10) * 10))
    if digito == 10:
        digito = 0
    return str(digito)


class FEPDF(object):
    "Interfaz para generar PDF de Factura Electrónica"

    def _agregar_campo(self, nombre, tipo, x1, y1, x2, y2,
                       font="Arial", size=12,
                       bold=False, italic=False, underline=False,
                       foreground="000000", background="FFFFFF",
                       align="L", text="", priority=0):
        """Agrego un campo al templates. Castea los campos a sus tipos"""

        self._elements.append({
            'name': nombre,
            'type': tipo,
            'x1': float(x1), 'y1': float(y1), 'x2': float(x2), 'y2': float(y2),
            'font': font, 'size': float(size),
            'bold': bold != "0",
            'italic': italic != "0",
            'underline': underline != "0",
            'foreground': int(foreground, 16),
            'background': int(background, 16),
            'align': align,
            'text': text,
            'priority': int(priority)
        })

    def _procesar_hoja(self, hoja, hojas, copia, tipo, letra, numero, barras,
                       li_items):
        """Metodo privado. Completa el template con info de la factura. Debe\
        ser llamada para cada hoja de cada copia.
        """

        f = self.template
        fact = self.factura

        f.add_page()
        f.set('copia', COPIAS[copia])
        f.set('hoja', str(hoja))
        f.set('hojas', str(hojas))
        f.set('pagina', 'Página {} de {}'.format(hoja, hojas))

        # El ultimo item esta reservado.
        s = ""
        if hoja > 1:
            s = 'Continúa de hoja {}. '.format(hoja - 1)
        if hojas > 1 and hoja < hojas:
            s += 'Continúa en hoja {}'.format(hoja + 1)
        f.set('Item.Descripcion{:02}'.format(self._lineas_max), s)

        # agreo los datos
        for dato in self.datos:
            if dato['pagina'] == 'P' and hoja != 1:
                continue
            if dato['pagina'] == 'U' and hojas != hoja:
                continue
            f.set(dato['campo'], dato['valor'])

        # Agrego los campos de la factura
        f.set('Numero', numero)
        f.set('Fecha', fmt_date(fact['fecha_cbte']))
        f.set('Vencimiento', fmt_date(fact['fecha_venc_pago']))
        f.set('Letra', letra)
        f.set('TipoCBTE', "COD. {:02}".format(fact['tipo_cbte']))
        f.set('Comprobante.L', tipo)
        f.set('FormaPago', fact["forma_pago"])
        f.set('Periodo.Desde', fmt_date(fact['fecha_serv_desde']))
        f.set('Periodo.Hasta', fmt_date(fact['fecha_serv_hasta']))
        if not fact['fecha_serv_desde']:
            f.set('PeriodoFacturadoL', '')

        f.set('Cliente.Id', fact['cliente_id'])
        f.set('Cliente.Nombre', fact['cliente_nombre'])
        f.set('Cliente.Domicilio', fact['cliente_domicilio'])
        f.set('Cliente.IVA', fact['cliente_iva'])
        f.set('Cliente.TipoDoc', "{}:".format(DOCS[fact['tipo_doc']]))
        if fact['tipo_doc'] in (80, 86):
            doc = fmt_cuit(fact['nro_doc'])
        else:
            doc = fact['nro_doc']
        f.set('Cliente.Doc', doc)

        f.set('Vendedor.Id', fact['vendedor_id'])
        f.set('Vendedor.Nombre', fact['vendedor_nombre'])
        if fact["obs_afip"]:
            s = f.split_multicell(fact["obs_afip"], 'ObsAFIP1')
            for i in range(len(s)):
                f.set('ObsAFIP{}'.format(i + 1), s[i])
        else:
            f.set('ObsAFIP.L', "")

        f.set('CAE', fact['cae'])
        f.set('CAE.Vencimiento', fmt_date(fact['fecha_vto_cae']))
        f.set('CodigoBarras', barras)
        f.set('CodigoBarrasLegible', barras)

        # Agrego los items en la hoja
        li = 0
        k = 0
        subtotal = Decimal(0)
        for it in li_items:
            k += 1
            if k > hoja * (self._lineas_max - 1):
                break

            # acumular subtotal (sin IVA facturas A)
            if it['importe']:
                subtotal += it['importe']
                if letra in ('A', 'M'):
                    subtotal -= it['imp_iva']

            # agregar el item si encuadra en la hoja especificada:
            if k > (hoja - 1) * (self._lineas_max - 1):
                li += 1
                f.set('Item.Cantidad{:02}'.format(li), fmt_qty(it['qty']))
                f.set('Item.Codigo{:02}'.format(li), it['codigo'])
                f.set('Item.Bonif{:02}'.format(li), fmt_num(it['bonif']))
                f.set('Item.Descripcion{:02}'.format(li), it['ds'])
                f.set('Item.Precio{:02}'.format(li), fmt_num(it['precio']))
                f.set('Item.Importe{:02}'.format(li), fmt_num(it['importe']))

                # recortar descripcion
                if it['umed'] and f.has_key("Item.Umed_ds01"):
                    umed_ds = UMEDS_DS.get(int(it['umed']))
                    s = f.split_multicell(umed_ds, 'Item.Umed_ds01')
                    f.set('Item.Umed_ds{:02}'.format(li), s[0])

                # solo discriminar IVA en A/M (mostrar tasa en B)
                if letra in ('A', 'M', 'B'):
                    f.set('Item.AlicuotaIva{:02}'.format(li),
                          fmt_iva(it['iva_id']))
                if letra in ('A', 'M'):
                    f.set('Item.ImporteIva{:02}'.format(li),
                          fmt_num(it['imp_iva']))

                # datos adicionales de items
                if it["_otros"]:
                    for key, val in it["_otros"].items():
                        f.set('Item.{}{:02}'.format(key, li), val)

        f.set('Total.L', 'Subtotal:')
        f.set('Total', fmt_num(subtotal))

        # limpio todas las etiqueta
        for k in ('imp_neto', 'imp_total',
                  'imp_iva',  'imp_trib', 'imp_op_ex',
                  'imp_tot_conc', 'imp_op_ex', 'IMP_IIBB', 'imp_iibb',
                  'imp_internos', 'EXENTO.L', 'subtotal.L'):
            f.set(k, "")

        for p in IVAS_DS.values():
            f.set('IVA{}.L'.format(p),  "")

    def _procesar_ultima_hoja(self, letra):
        """Metodo privado. Completa el template con info sobre totales. Debe\
        ser llamada en la ultima hoja de cada copia y despues de _procesar_hoja
        """

        f = self.template
        fact = self.factura

        # agrego otros tributos
        lit = 0
        for it in fact['tributos']:
            lit += 1
            if it['desc']:
                f.set('Tributo.Descripcion{:02}'.format(lit), it['desc'])
            else:
                f.set('Tributo.Descripcion{:02}'.format(lit),
                      self.tributos_ds[it['tributo_id']])

            f.set('Tributo.BaseImp{:02}'.format(lit), fmt_num(it['base_imp']))
            f.set('Tributo.Alicuota{:02}'.format(lit),
                  fmt_num(it['alic']) + "%")
            f.set('Tributo.Importe{:02}'.format(lit), fmt_imp(it['importe']))

        # Muestro el IVA cuando corresponda
        if letra in ('A', 'M'):
            for iva in fact['ivas']:
                p = IVAS_DS[iva['iva_id']]
                f.set('IVA{}.L'.format(p),
                      "IVA {:02}%".format(p).replace(".", ","))
                f.set('NETO{}'.format(p), fmt_num(iva['base_imp']))
                f.set('IVA{}'.format(p), fmt_num(iva['importe']))

        # reiniciar el subtotal neto, independiente de detalles:
        subtotal = fact['imp_neto']
        # agregar IVA al subtotal si no es factura A
        if letra not in ('A', 'M'):
            subtotal += Decimal(fact['imp_iva'])

        # al subtotal neto sumo exento y no gravado:
        subtotal += Decimal(fact['imp_tot_conc'])
        subtotal += Decimal(fact['imp_op_ex'])
        # importes generales de IVA y netos gravado / no gravado
        f.set("subtotal.L",  "Subtotal:")
        f.set('subtotal', fmt_num(subtotal))
        f.set('imp_iva', fmt_num(fact.get('imp_iva')))
        f.set('imp_trib', fmt_num(fact.get('imp_trib')))
        f.set('imp_tot_conc', fmt_num(fact['imp_tot_conc']))
        f.set('imp_op_ex', fmt_num(fact['imp_op_ex']))
        f.set('Total.L', 'Total:')
        f.set('Total', fmt_num(fact['imp_total']))

    def __init__(self, papel, orientacion, cuit, copias, lineas_max=36,
                 fmt_cantidad="0.2", fmt_precio="0.2"):
        """Constructor. Toma los parametros principales para la creaciond el PDF
        :params (str) papel: El tamaño de papel: A5, A4, letter, o legal.
        :params (str) orientacion: Debe ser P o L.
        :params (int) cuit:
        :params (int) copias:
        :params (int) lienas_max: maximo items en la factura [5: 50]. Debe\
        tener en cuenta que esas lineas deben entrar en el tamaño de hoja.
        :param (str) fmt_cantidad: Formato para imprimir las cantidad. Por\
        defecto son dos decimales
        :param (str) fmt_precio: Formato para imprimir las precios. Por\
        defecto son dos decimales
        """

        assert papel in PAPER_SIZE,\
            "papel debe ser {}".format(PAPER_SIZE.join(", "))
        assert orientacion in ("P", "L"), "orientacion debe ser 'P' o 'L'"
        assert 1 <= copias <= 3, "Copias debe ser 1, 2 o 3"
        assert type(cuit) is int, "cuit debe ser un numero"
        assert 5 <= lineas_max <= 50, "lineas_max debe estar en [5, 50]"

        self.factura = None
        self.template = None   # fpdf Template object
        self._papel = papel
        self._orientacion = orientacion
        self._copias = copias
        self._elements = []
        self._lineas_max = lineas_max
        self.cuit = cuit
        self.datos = []

        global FMTCANTIDAD, FMTPRECIO
        FMTCANTIDAD = fmt_cantidad
        FMTPRECIO = fmt_precio

    def crear_factura(
            self, tipo_doc=80, nro_doc="", tipo_cbte=1, punto_vta=0,
            cbte_nro=0, imp_total=0.00, imp_tot_conc=0.00, imp_neto=0.00,
            imp_iva=0.00, imp_trib=0.00, imp_op_ex=0.00, fecha_cbte="",
            fecha_venc_pago="", fecha_serv_desde=None, fecha_serv_hasta=None,
            cae="", fecha_vto_cae="", cliente_iva='',
            cliente_id='', cliente_nombre="", cliente_domicilio="",
            vendedor_id='', vendedor_nombre='',
            obs_comerciales="", obs_generales="", forma_pago="",
            obs_afip="", **args):
        """Crea el objeto factura, que no es mas que un simple dict. Luego de\
        ser creado puede accederse en el atributo ``factura`` para reemplazar\
        algun valor

        Permite cualquier cantidad de atributos kwargs, pero solo se usaran\
        los que se listan en este apartado. Los demas se ignoraran sin ningun\
        mensaje de advertencia

        * Info de la empresa
        :param (int) tipo_cbte: Codigo del tipo de comprobante.
        :param (int) punto_vta: Punto de venta.
        :param (int) cbte_nro: Numero del comprobante.
        :param vendedor_id: Codigo del vendedor
        :param vendedor_nombre: Nombre del vendedor

        * Totales
        :param imp_trib: Importe de otros tributos (incluyendo percepciones\
        de IVA, retenciones, IVA no inscripto, etc.)
        :param imp_iva: Importe del IVA liquidado (igual a la suma de\
        importe_iva para todas las alícutoas).
        :param imp_neto: Importe neto (gravado por el IVA) de la factura\
        (igual a la suma de base_imp para todas las alicuotas)
        :param imp_tot_conc: Importe total de conceptos no gravados por el IVA
        :param imp_op_ex: Importe de operacion excentas de IVA
        :param imp_total: El total de la factura

        * Fechas
        :param (date) fecha_cbte: fecha del comprobante
        :param (date) fecha_venc_pago: vencimiento de pago
        :param (date) fecha_serv_desde: inicio de servicio
        :param (date) fecha_serv_hasta: fin del servicio

        * Informacion del cliente
        :param cliente_id: Codigo del cliente
        :param cliente_nombre: Nombre del cliente.
        :param cliente_domicilio: Domicilio del cliente
        :param (str) cliente_iva: Condicion de IVA del cliente. \
        Ej: Responsable Inscripto
        :param (int) tipo_doc: Codigo del tipo de documento
        :param (int) nro_doc: Docuemento del cliente
        :param (str) obs_comerciales: Observaciones comerciales
        :param (str) obs_generales: Observaciones generales
        :param (str) forma_pago: Forma de pago. Ej: Contado

        * AFIP
        :param (str) cae: CAE obtenido de AFIP
        :param (str) obs_afip: Observaciones obtenida de AFIP.
        :param (str o date) fecha_vto_cae: fecha en format YYYYMMDD
        """

        if isinstance(fecha_vto_cae, str):
            fecha_vto_cae = datetime.date(
                int(fecha_vto_cae[0:4]),
                int(fecha_vto_cae[4:6]),
                int(fecha_vto_cae[6:8]))

        self.factura = {
            'tipo_cbte': int(tipo_cbte),
            'punto_vta': int(punto_vta),
            'cbte_nro': int(cbte_nro),
            'imp_trib': Decimal(imp_trib),
            'imp_iva': Decimal(imp_iva),
            'imp_neto': Decimal(imp_neto),
            'imp_tot_conc': Decimal(imp_tot_conc),
            'imp_op_ex': Decimal(imp_op_ex),
            'imp_total': Decimal(imp_total),
            'fecha_cbte': fecha_cbte,
            'fecha_venc_pago': fecha_venc_pago,
            'fecha_serv_desde': fecha_serv_desde,
            'fecha_serv_hasta': fecha_serv_hasta,
            'cliente_id': cliente_id,
            'cliente_nombre': cliente_nombre,
            'cliente_domicilio': cliente_domicilio,
            'cliente_iva': cliente_iva,
            'tipo_doc': int(tipo_doc),
            'nro_doc': int(nro_doc),
            'vendedor_id': vendedor_id,
            'vendedor_nombre': vendedor_nombre,
            'obs_comerciales': obs_comerciales,
            'obs_generales': obs_generales,
            'forma_pago': forma_pago,
            'cae': cae,
            'fecha_vto_cae': fecha_vto_cae,
            'obs_afip': obs_afip,
            'cbtes_asoc': [],
            'tributos': [],
            'ivas': [],
            'detalles': []
        }
        tipo, letra, numero = fmt_fact(
            self.factura['tipo_cbte'],
            self.factura['punto_vta'],
            self.factura['cbte_nro'])

        self.template = self.get_template_class()(
            elements=self._elements,
            format=self._papel,
            orientation=self._orientacion,
            title="{} {} {}".format(tipo, letra, numero),
            author="CUIT {}".format(self.cuit),
            subject="CAE {}".format(self.factura['cae']),
            keywords="AFIP Factura Electrónica",
            creator='fepdf {}'.format(VERSION))

    def get_template_class(self):
        return Template

    def agregar_dato(self, campo, valor, pagina=None):
        """Agrego un dato a la factura. Cuando se emita el PDF, se buscara un
        campo llamado `campo` y se le dara el valor `valor`

        :param (str) campo: el nombre del campo
        :param (str) valor: el valor del campo.
        :param (str) pagina: 'P' o 'U' indicando si imprime en la primero o \
        ultima correpondientemnete. Caso contrario, imprime en todas.
        """

        if pagina not in ("P", "U"):
            pagina = None

        self.datos.append({'campo': campo, 'valor': valor, 'pagina': pagina})

    def agregar_item(self, codigo, ds, qty, umed, precio,
                     bonif, iva_id, imp_iva, importe, **kwargs):
        """Agrego un item a una factura. Acepta cualquier cantidad de\
        parametros que serán impresos sobre la etiqueta\
        ``Item.<parametro><nro_liena>``

        Los parametros obligatorios son los siguintes
        :param codigo: el codigo del articulo.
        :param (str) ds: La descripcion del articulo.
        :param qty: Cantidad de articulos vendidos
        :param umed: codigo de unidad de medida.
        :param precio: precio unitario del articulo. Si es factura A, no debe\
        incluir IVA.
        :param bonif: Descuento unitario del articulo. Si es factura A, no\
        debe incluir IVA.
        :param imp_iva: El iva total
        :param importe: El total del detalle.
        """

        self.factura['detalles'].append({
            'codigo': codigo,
            'ds': ds,
            'qty': qty,
            'umed': umed,
            'precio': Decimal(precio),
            'bonif': Decimal(bonif),
            'iva_id': iva_id,
            'imp_iva': Decimal(imp_iva),
            'importe': Decimal(importe),
            '_otros': kwargs
        })

    def agregar_cmp_asoc(self, tipo, pto_venta, numero):
        """Agrego un comprobante asociado a una factura

        :param (int) tipo: El codigo del tipo del comprobante.\
        Ej: 1 para Factura A
        :param (int) pto_venta: El punto de venta
        :param (int) numero: El numero de la factura
        """

        self.factura['cbtes_asoc'].append(
            " ".join(fmt_fact(tipo, pto_venta, numero)))

    def agregar_tributo(self, tributo_id, desc, base_imp=0, alic=0, importe=0):
        """Agrego un tributo a una factura"""

        self.factura['tributos'].append({
            'tributo_id': tributo_id,
            'desc': desc,
            'base_imp': base_imp,
            'alic': alic,
            'importe': importe
        })

    def agregar_iva(self, iva_id, base_imp, importe):
        """Agrego un tributo de IVA a la factura. base_imp y importe se castean\
        Decimal, por lo que pueden ser de cualquier tipo que acepte el
        constructor de Decimal.

        :param (int) iva_id: el codigo de la alicuota iva.
        :param base_imp: base imponible. Ej. Si la venta se\
        realizo por $121 con iva del 21%, aqui debe ir $100
        :param importe: el importe del iva. Ej. Si la venta\
        se realizo por $121 con iva del 21%, aqui debe ir $21
        """

        self.factura['ivas'].append({
            'iva_id': iva_id,
            'base_imp': Decimal(base_imp),
            'importe': Decimal(importe)
        })

    def cargar_formato(self, archivo):
        """Cargo el formato de campos a generar desde una planilla CSV"""

        assert os.path.isfile(archivo), "{} no es un archivo".format(archivo)

        with open(archivo) as template:
            for row in template.read().splitlines():
                if not row or row.startswith("#"):
                    continue
                args = []
                for val in row.split(";"):
                    val = val.strip()
                    if val.startswith("'") or val.startswith('"'):
                        val = val[1: -1]
                    args.append(val)

                assert len(args) == 16, MSGS["tmpl_nber_values"]
                self._agregar_campo(*args)

    def render(self, archivo):
        """Generar archivo de salida en formato PDF"""
        return self.template.render(archivo, "F")

    def procesar_plantilla(self):
        """LLena el template con la info de la factura"""

        assert self._elements, "No se encontraron campos. Llamo a "\
            "cargar_formato()?"
        tipo, letra, numero = fmt_fact(
            self.factura['tipo_cbte'],
            self.factura['punto_vta'],
            self.factura['cbte_nro'])
        fact = self.factura
        f = self.template

        #
        # agrego un item por linea. Los atributos van en la primera
        #
        lineas = 0
        li_items = []
        for it in fact['detalles']:
            for line in f.split_multicell(it["ds"], 'Item.Descripcion01'):
                d = defaultdict(str)
                d["ds"] = line
                li_items.append(d)
            _it = it.copy()
            del _it["ds"]
            li_items[-1].update(_it)

        #
        # Agrego las Obs como items
        #
        if fact['obs_generales']:
            obs = "Observaciones: {}".format(fact['obs_generales'])
            for ds in f.split_multicell(obs, 'Item.Descripcion01'):
                d = defaultdict(str)
                d["ds"] = ds
                li_items.append(d)

        if fact['obs_comerciales']:
            obs = "Observaciones Comerciales: {}".format(
                fact['obs_comerciales'])
            for ds in f.split_multicell(obs, 'Item.Descripcion01'):
                d = defaultdict(str)
                d["ds"] = ds
                li_items.append(d)

        #
        # agrego comprobantes asociados como items
        #
        if fact["cbtes_asoc"]:
            obs = "Comprobantes Asociados: {}".format(
                ', '.join(fact["cbtes_asoc"]))
            for ds in f.split_multicell(obs, 'Item.Descripcion01'):
                d = defaultdict(str)
                d["ds"] = ds
                li_items.append(d)

        #
        # Observaciones de AFIP
        #
        if fact['obs_afip']:
            if letra in ('A', 'M'):
                fact['obs_afip'] += MSGS["no_iva"]
        #
        # Proceso el template
        #
        hojas = math.ceil(len(li_items) / (self._lineas_max - 1))
        barras = '{}{:02}{:04}{}{}'.format(
            self.cuit,
            int(fact['tipo_cbte']),
            int(fact['punto_vta']),
            fact['cae'],
            fact['fecha_vto_cae'].strftime("%Y%m%d"))
        barras += digito_verificador_modulo10(barras)

        for copia in range(1, self._copias + 1):
            for hoja in range(1, hojas + 1):
                self._procesar_hoja(
                    hoja, hojas, copia, tipo, letra, numero, barras,
                    li_items)

            # Si es la ultima hoja, agrego los totales
            self._procesar_ultima_hoja(letra)
