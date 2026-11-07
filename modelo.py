"""
modelo.py
=========
Clases que representan los datos del problema y el ESTADO de la búsqueda.

Datos (se leen de los archivos .txt):
    Profesor, Salon, Franja, Curso

Búsqueda:
    Asignacion -> "la clase X va en la franja Y y el salón Z"
    Estado     -> conjunto de asignaciones hechas hasta el momento

Representación del estado
-------------------------
Las clases se programan SIEMPRE en el mismo orden (el orden del archivo
cursos.txt). Por eso un estado es simplemente la lista de asignaciones de las
primeras k clases:

    Estado vacío          -> ninguna clase asignada (estado inicial)
    Estado con k = N      -> todas las clases asignadas (estado meta)

Con este orden fijo cada estado se puede alcanzar de UNA sola manera, así que
no hay estados repetidos y no hace falta una lista de "visitados".
"""


class Profesor:
    """Un profesor. 'no_disponible' guarda los ids de las franjas que marcó
    como no disponibles (restricción blanda)."""

    def __init__(self, id, nombre, no_disponible=None):
        self.id = id
        self.nombre = nombre
        self.no_disponible = set(no_disponible) if no_disponible else set()

    def __str__(self):
        return self.nombre


class Salon:
    """Un salón de clases."""

    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre

    def __str__(self):
        return self.nombre


class Franja:
    """Una franja horaria: un día y una hora (por ejemplo Lunes 07-09).

    'posicion' es el puesto de la franja dentro de su día (0 = la primera
    del día, 1 = la segunda, ...). Sirve para saber qué franjas son
    consecutivas. La calcula el lector de archivos.
    """

    def __init__(self, id, dia, hora, posicion=0):
        self.id = id
        self.dia = dia
        self.hora = hora
        self.posicion = posicion

    def __str__(self):
        return f"{self.dia} {self.hora}"


class Curso:
    """Una clase que debe programarse (es la 'variable' del CSP).

    'profesor' empieza en None y se llena con lector.enlazar_datos(), que
    cambia el id del profesor por el objeto Profesor correspondiente.
    """

    def __init__(self, id, materia, id_profesor, grupo):
        self.id = id
        self.materia = materia
        self.id_profesor = id_profesor
        self.grupo = grupo
        self.profesor = None

    def __str__(self):
        return f"{self.materia} ({self.grupo})"


class Asignacion:
    """Decisión tomada para un curso: en qué franja y en qué salón se dicta."""

    def __init__(self, curso, franja, salon):
        self.curso = curso
        self.franja = franja
        self.salon = salon

    def __str__(self):
        return f"{self.curso.materia} -> {self.franja}, {self.salon}"


class Estado:
    """Estado de la búsqueda: tupla de asignaciones ya hechas.

    Es inmutable: agregar() NO modifica el estado, devuelve uno nuevo.
    Así cada nodo de la búsqueda conserva su propio estado sin mezclarse.
    """

    def __init__(self, asignaciones=()):
        self.asignaciones = tuple(asignaciones)

    def agregar(self, asignacion):
        """Devuelve un estado nuevo con una asignación más."""
        return Estado(self.asignaciones + (asignacion,))

    def __len__(self):
        """Cantidad de clases ya asignadas."""
        return len(self.asignaciones)

    def a_grilla(self):
        """Organiza el horario para dibujarlo como tabla.

        Devuelve un diccionario {(dia, hora): [Asignacion, ...]}.
        Es una LISTA porque en la misma franja pueden dictarse varias clases
        a la vez (en salones distintos, con profesores y grupos distintos).
        Las franjas que no aparecen en el diccionario están libres.
        """
        grilla = {}
        for a in self.asignaciones:
            grilla.setdefault((a.franja.dia, a.franja.hora), []).append(a)
        return grilla

    def __str__(self):
        if not self.asignaciones:
            return "(estado vacío)"
        return "\n".join(str(a) for a in self.asignaciones)


def dias_de(franjas):
    """Días distintos, en el orden en que aparecen en franjas.txt
    (columnas de la tabla de horario)."""
    dias = []
    for f in franjas:
        if f.dia not in dias:
            dias.append(f.dia)
    return dias


def horas_de(franjas):
    """Horas distintas, en el orden en que aparecen en franjas.txt
    (filas de la tabla de horario)."""
    horas = []
    for f in franjas:
        if f.hora not in horas:
            horas.append(f.hora)
    return horas
