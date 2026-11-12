# Penalizaciones (se suman al costo base de 1 por asignación)
PESO_NO_DISPONIBLE = 5
PESO_CONSECUTIVAS = 3

# N: máximo de clases consecutivas que puede tener un grupo en un día
MAX_CONSECUTIVAS = 3


# ----------------------------------------------------------------------
# Restricciones duras
# ----------------------------------------------------------------------

def curso_ya_asignado(estado, curso):
    for a in estado.asignaciones:
        if a.curso.id == curso.id:
            return True
    return False


def hay_conflicto_salon(estado, franja, salon):
    for a in estado.asignaciones:
        if a.franja.id == franja.id and a.salon.id == salon.id:
            return True
    return False


def hay_conflicto_profesor(estado, curso, franja):
    for a in estado.asignaciones:
        if a.franja.id == franja.id and a.curso.profesor.id == curso.profesor.id:
            return True
    return False


def hay_conflicto_grupo(estado, curso, franja):
    for a in estado.asignaciones:
        if a.franja.id == franja.id and a.curso.grupo == curso.grupo:
            return True
    return False


def cumple_restricciones_duras(estado, asignacion):
    return (
        not curso_ya_asignado(estado, asignacion.curso)
        and not hay_conflicto_salon(estado, asignacion.franja, asignacion.salon)
        and not hay_conflicto_profesor(estado, asignacion.curso, asignacion.franja)
        and not hay_conflicto_grupo(estado, asignacion.curso, asignacion.franja)
    )


def es_solucion_valida(estado, cursos):
    if len(estado) != len(cursos):
        return False
    ids_asignados = {a.curso.id for a in estado.asignaciones}
    if ids_asignados != {c.id for c in cursos}:
        return False

    # Se reconstruye el horario asignación por asignación revisando conflictos
    parcial = type(estado)()
    for a in estado.asignaciones:
        if not cumple_restricciones_duras(parcial, a):
            return False
        parcial = parcial.agregar(a)
    return True


# ----------------------------------------------------------------------
# Restricciones blandas
# ----------------------------------------------------------------------

def penalizacion_disponibilidad(asignacion):
    """Blanda 1: penaliza si la franja está marcada como no disponible
    para el profesor del curso."""
    if asignacion.franja.id in asignacion.curso.profesor.no_disponible:
        return PESO_NO_DISPONIBLE
    return 0


def _exceso_consecutivas(posiciones, maximo):
    exceso = 0
    racha = 0
    anterior = None
    for p in sorted(posiciones):
        if anterior is not None and p == anterior + 1:
            racha += 1
        else:
            exceso += max(0, racha - maximo)
            racha = 1
        anterior = p
    exceso += max(0, racha - maximo)
    return exceso


def penalizacion_consecutivas(estado, asignacion, maximo=MAX_CONSECUTIVAS):
    """Blanda 2: penaliza si la nueva clase hace que el grupo tenga más de
    'maximo' clases seguidas ese día."""
    grupo = asignacion.curso.grupo
    dia = asignacion.franja.dia
    antes = [a.franja.posicion for a in estado.asignaciones
             if a.curso.grupo == grupo and a.franja.dia == dia]
    despues = antes + [asignacion.franja.posicion]
    aumento = _exceso_consecutivas(despues, maximo) - _exceso_consecutivas(antes, maximo)
    return PESO_CONSECUTIVAS * aumento


def penalizacion_blanda(estado, asignacion, maximo=MAX_CONSECUTIVAS):
    return (penalizacion_disponibilidad(asignacion)
            + penalizacion_consecutivas(estado, asignacion, maximo))
