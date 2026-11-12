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

    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre

    def __str__(self):
        return self.nombre


class Franja:

    def __init__(self, id, dia, hora, posicion=0):
        self.id = id
        self.dia = dia
        self.hora = hora
        self.posicion = posicion

    def __str__(self):
        return f"{self.dia} {self.hora}"


class Curso:

    def __init__(self, id, materia, id_profesor, grupo):
        self.id = id
        self.materia = materia
        self.id_profesor = id_profesor
        self.grupo = grupo
        self.profesor = None

    def __str__(self):
        return f"{self.materia} ({self.grupo})"


class Asignacion:

    def __init__(self, curso, franja, salon):
        self.curso = curso
        self.franja = franja
        self.salon = salon

    def __str__(self):
        return f"{self.curso.materia} -> {self.franja}, {self.salon}"


class Estado:

    def __init__(self, asignaciones=()):
        self.asignaciones = tuple(asignaciones)

    def agregar(self, asignacion):
        """Devuelve un estado nuevo con una asignación más."""
        return Estado(self.asignaciones + (asignacion,))

    def __len__(self):
        """Cantidad de clases ya asignadas."""
        return len(self.asignaciones)

    def a_grilla(self):
        grilla = {}
        for a in self.asignaciones:
            grilla.setdefault((a.franja.dia, a.franja.hora), []).append(a)
        return grilla

    def __str__(self):
        if not self.asignaciones:
            return "(estado vacío)"
        return "\n".join(str(a) for a in self.asignaciones)


def dias_de(franjas):
    dias = []
    for f in franjas:
        if f.dia not in dias:
            dias.append(f.dia)
    return dias


def horas_de(franjas):
    horas = []
    for f in franjas:
        if f.hora not in horas:
            horas.append(f.hora)
    return horas
