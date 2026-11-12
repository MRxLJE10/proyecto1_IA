from cola_prioridad import ColaPrioridad
import time
from cola_prioridad import ColaPrioridad, ColaFIFO
from estadisticas import Resultado

MAX_NODOS_DEFECTO = 100000

MOTIVO_ENCONTRADA = "Solución encontrada"
MOTIVO_LIMITE = "Se superó el límite de nodos"
MOTIVO_SIN_SOLUCION = "No existe solución (se agotó el espacio de búsqueda)"


def _crear_resultado(nombre, problema, solucion, explorados, generados, inicio, motivo):
    tiempo = time.perf_counter() - inicio
    penalizacion = 0
    costo = 0
    if solucion is not None:
        penalizacion = problema.penalizacion_total(solucion)
        costo = problema.costo_total(solucion)
    return Resultado(nombre, solucion, explorados, generados, tiempo,
                     motivo, penalizacion, costo)


# ----------------------------------------------------------------------
# 1. Búsqueda en amplitud (BFS)
# ----------------------------------------------------------------------

def busqueda_amplitud(problema, max_nodos=MAX_NODOS_DEFECTO):
    inicio = time.perf_counter()
    explorados = 0
    generados = 1  # el estado inicial
    solucion = None
    motivo = ""
    frontera = ColaFIFO()
    frontera.agregar(problema.estado_inicial())

    while len(frontera) > 0:
        if explorados >= max_nodos:
            motivo = MOTIVO_LIMITE
            break

        estado = frontera.extraer_primero()          # el más antiguo de la cola
        explorados += 1

        if problema.es_meta(estado):
            solucion = estado
            motivo = MOTIVO_ENCONTRADA
            break

        for hijo, _costo in problema.sucesores(estado):
            frontera.agregar(hijo)            # los hijos van al final de la cola
            generados += 1

    if motivo == "":
        motivo = MOTIVO_SIN_SOLUCION         # la cola se vació sin hallar meta

    return _crear_resultado("BFS (amplitud)", problema, solucion,
                            explorados, generados, inicio, motivo)


# ----------------------------------------------------------------------
# 2. Búsqueda de costo uniforme (UCS)
# ----------------------------------------------------------------------

def busqueda_costo_uniforme(problema, max_nodos=MAX_NODOS_DEFECTO):
    inicio = time.perf_counter()
    explorados = 0
    generados = 1
    solucion = None
    motivo = ""

    # La prioridad es g, el valor guarda (g, estado) para poder usar g al expandir.
    frontera = ColaPrioridad()
    frontera.agregar(0, (0, problema.estado_inicial()))

    while len(frontera) > 0:
        if explorados >= max_nodos:
            motivo = MOTIVO_LIMITE
            break

        costo, estado = frontera.extraer_minimo()   # el de menor costo
        explorados += 1

        if problema.es_meta(estado):
            solucion = estado
            motivo = MOTIVO_ENCONTRADA
            break

        for hijo, costo_paso in problema.sucesores(estado):
            g_hijo = costo + costo_paso
            frontera.agregar(g_hijo, (g_hijo, hijo))
            generados += 1

    if motivo == "":
        motivo = MOTIVO_SIN_SOLUCION

    return _crear_resultado("Costo uniforme", problema, solucion,
                            explorados, generados, inicio, motivo)


# ----------------------------------------------------------------------
# 3. Búsqueda en profundidad iterativa (IDS)
# ----------------------------------------------------------------------

class _LimiteExcedido(Exception):
    pass


class _BusquedaLimitada:

    def __init__(self, problema, max_nodos):
        self.problema = problema
        self.max_nodos = max_nodos
        self.explorados = 0
        self.generados = 1

    def visitar(self, estado, limite):
        if self.explorados >= self.max_nodos:
            raise _LimiteExcedido()
        self.explorados += 1

        if self.problema.es_meta(estado):
            return estado
        if limite == 0:                       # no se puede bajar más
            return None

        for hijo, _costo in self.problema.sucesores(estado):
            self.generados += 1
            encontrado = self.visitar(hijo, limite - 1)
            if encontrado is not None:
                return encontrado
        return None


def busqueda_profundidad_iterativa(problema, max_nodos=MAX_NODOS_DEFECTO):
    inicio = time.perf_counter()
    busqueda = _BusquedaLimitada(problema, max_nodos)
    solucion = None
    motivo = ""

    try:
        for limite in range(len(problema.cursos) + 1):
            solucion = busqueda.visitar(problema.estado_inicial(), limite)
            if solucion is not None:
                motivo = MOTIVO_ENCONTRADA
                break
        if motivo == "":
            motivo = MOTIVO_SIN_SOLUCION     # ningún límite llevó a una meta
    except _LimiteExcedido:
        motivo = MOTIVO_LIMITE

    return _crear_resultado("Profundidad iterativa", problema, solucion,
                            busqueda.explorados, busqueda.generados, inicio, motivo)


# ----------------------------------------------------------------------
# Interfaz: nombre que se muestra -> función
# ----------------------------------------------------------------------

ALGORITMOS_NO_INFORMADOS = {
    "BFS (amplitud)": busqueda_amplitud,
    "Costo uniforme": busqueda_costo_uniforme,
    "Profundidad iterativa": busqueda_profundidad_iterativa,
}
