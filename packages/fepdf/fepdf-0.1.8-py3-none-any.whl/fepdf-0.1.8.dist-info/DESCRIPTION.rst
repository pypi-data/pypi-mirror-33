=====
FEPDF
=====

Generacion en PDF de facturas electrónicas. Módulo inspirado de `pyfepdf <https://github.com/reingart/pyafipws/blob/master/pyfepdf.py>`_ de `Mariano Reigart <https://twitter.com/reingart>`_.

pyfepdf es uno de los modulos del excelente proyecto PyAFIPWS. Si aun no lo  conoces deberias mirarlo, antes de utilizar esta utilidad. Si bien el proyecto entero funciona muy bien, hemos encontrado algunas defeciencias.

---------
Objetivos
---------

Buscamos realizar las siguientes mejoras comparadas con el modulo original de reingart.

* Funcionamiento exclusivo en Python 3.x (Sin soporte a Python 2.x)
* Cumplimiento de las recomendaciones de PEP8
* Facilidad de instalcion utilizando pip
* Mejora en la documentación.
* Impresion en tamaño de papel A5
* Simplificacion de codigo dejango solo las etiquetas necesarias para emitir facturas dentro del mercado interno.

-----------
Instalación
-----------

Instalable desde PyPI con el siguiente comnado

``$ pip install fepdf``

-----------
Guia de Uso
-----------

Hemos mantenido la misma interfaz del proyecto original, pero utilizando nombres *undescore*, por lo que, por ej. el metodo ``CrearFactura`` ahora es ``crear_factura``.

En el ``fepdf.py`` hay una pequeña guia que le servirá para utilizar este modulo correctamente


