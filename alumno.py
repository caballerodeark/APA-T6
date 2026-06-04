"""
Módulo para la gestión y tratamiento de notas de alumnos.
Autor: Guillem Pérez Sánchez
QP 2026
"""

import re
import doctest


class Alumno:
    """
    Clase usada para el tratamiento de las notas de los alumnos. Cada uno
    incluye los atributos siguientes:

    numIden:   Número de identificación. Es un número entero que, en caso
               de no indicarse, toma el valor por defecto 'numIden=-1'.
    nombre:    Nombre completo del alumno.
    notas:     Lista de números reales con las distintas notas de cada alumno.
    """

    def __init__(self, nombre, numIden=-1, notas=[]):
        self.numIden = numIden
        self.nombre = nombre
        self.notas = [nota for nota in notas]

    def __add__(self, other):
        """
        Devuelve un nuevo objeto 'Alumno' con una lista de notas ampliada con
        el valor pasado como argumento. De este modo, añadir una nota a un
        Alumno se realiza con la orden 'alumno += nota'.
        """
        return Alumno(self.nombre, self.numIden, self.notas + [other])

    def media(self):
        """
        Devuelve la nota media del alumno.
        """
        return sum(self.notas) / len(self.notas) if self.notas else 0

    def __repr__(self):
        """
        Devuelve la representación 'oficial' del alumno. A partir de copia
        y pega de la cadena obtenida es posible crear un nuevo Alumno idéntico.
        """
        return f'Alumno("{self.nombre}", {self.numIden!r}, {self.notas!r})'

    def __str__(self):
        """
        Devuelve la representación 'bonita' del alumno. Visualiza en tres
        columnas separas por tabulador el número de identificación, el nombre
        completo y la nota media del alumno con un decimal.
        """
        return f'{self.numIden}\t{self.nombre}\t{self.media():.1f}'


def leeAlumnos(ficAlum):
    """
    Lee un fichero de texto con los datos de todos los alumnos y devuelve un
    diccionario en el que la clave sea el nombre de cada alumno y su contenido
    el objeto Alumno correspondiente.

    >>> from alumno import leeAlumnos
    >>> alumnos = leeAlumnos('alumnos.txt')
    >>> for alumno in alumnos:
    ...     print(alumnos[alumno])
    ...
    171     Blanca Agirrebarrenetse 9.5
    23      Carles Balcells de Lara 4.9
    68      David Garcia Fuster     7.0
    """
    dicc_alumnos = {}
    
    # Expresión regular para capturar ID (opcional), Nombre y Notas consecutivas
    patron = re.compile(
        r'^\s*(?P<id>\d+)?\s+(?P<nombre>[A-Za-zÀ-ÿ\s]+?)\s+(?P<notas>[\d.\s]+)$'
    )

    with open(ficAlum, 'r', encoding='utf-8') as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            
            match = patron.match(linea)
            if match:
                id_str = match.group('id')
                numIden = int(id_str) if id_str else -1
                nombre = match.group('nombre').strip()
                
                # Extraer todas las notas decimales o enteras del bloque final
                notas_str = re.findall(r'\d+(?:\.\d+)?', match.group('notas'))
                notas = [float(n) for n in notas_str]
                
                dicc_alumnos[nombre] = Alumno(nombre, numIden, notas)
                
    return dicc_alumnos


if __name__ == '__main__':
    # Ejecución por defecto en modo verboso para la generación del reporte
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE, verbose=True)
