"""
busqueda_no_informada.py
========================
Tres algoritmos de búsqueda NO informada (no usan ninguna heurística):

  1. busqueda_amplitud            (BFS)  -> cola FIFO
  2. busqueda_costo_uniforme      (UCS)  -> cola de prioridad por costo
  3. busqueda_profundidad_iterativa (IDS) -> profundidad limitada, límite creciente

Todos reciben un ProblemaHorarios y devuelven un Resultado (estadisticas.py).
Todos cuentan "nodos explorados" de la misma forma: cada vez que un estado se
saca de la frontera (o se visita) para preguntar si es la meta.

LÍMITE DE NODOS: el espacio de búsqueda crece muy rápido con el número de
clases. Para que el programa no se quede pegado, cada algoritmo se detiene si
explora 'max_nodos' nodos; en ese caso el Resultado indica que no encontró
solución por haber superado el límite.
"""

import heapq
import time
from collections import deque

from estadisticas import Resultado

MAX_NODOS_DEFECTO = 100000

MOTIVO_ENCONTRADA = "Solución encontrada"
MOTIVO_LIMITE = "Se superó el límite de nodos"
MOTIVO_SIN_SOLUCION = "No existe solución (se agotó el espacio de búsqueda)"


def _crear_resultado(nombre, problema, solucion, explorados, generados, inicio, motivo):
    """Arma el Resultado final calculando el tiempo y, si hay solución,
    su penalización y su costo."""
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
    """Explora el árbol nivel por nivel: primero todos los estados con 1 clase
    asignada, luego los de 2 clases, etc. Usa una cola FIFO (el primero que
    entra es el primero que sale).

    Devuelve la primera solución que encuentra (la de menor profundidad, que
    aquí siempre es la misma para todas). NO tiene en cuenta las penalizaciones
    blandas, por eso su solución puede violar restricciones blandas.
    """
    inicio = time.perf_counter()
    explorados = 0
    generados = 1  # el estado inicial
    solucion = None
    motivo = ""

    frontera = deque([problema.estado_inicial()])

    while frontera:
        if explorados >= max_nodos:
            motivo = MOTIVO_LIMITE
            break

        estado = frontera.popleft()          # el más antiguo de la cola
        explorados += 1

        if problema.es_meta(estado):
            solucion = estado
            motivo = MOTIVO_ENCONTRADA
            break

        for hijo, _costo in problema.sucesores(estado):
            frontera.append(hijo)            # los hijos van al final de la cola
            generados += 1

    if motivo == "":
        motivo = MOTIVO_SIN_SOLUCION         # la cola se vació sin hallar meta

    return _crear_resultado("BFS (amplitud)", problema, solucion,
                            explorados, generados, inicio, motivo)


# ----------------------------------------------------------------------
# 2. Búsqueda de costo uniforme (UCS)
# ----------------------------------------------------------------------

def busqueda_costo_uniforme(problema, max_nodos=MAX_NODOS_DEFECTO):
    """Siempre expande el estado con MENOR costo acumulado g (clases asignadas
    + penalizaciones blandas). Usa una cola de prioridad.

    Como el costo de cada paso es positivo, la primera meta que sale de la
    cola es la de menor costo total: el horario que menos restricciones
    blandas viola. La prueba de meta se hace al SACAR el estado de la cola
    (no al generarlo), que es lo que garantiza esa optimalidad.
    """
    inicio = time.perf_counter()
    explorados = 0
    generados = 1
    solucion = None
    motivo = ""

    # Cada elemento es (costo, desempate, estado). El 'desempate' es un
    # contador que evita comparar dos Estado cuando hay costos iguales y hace
    # que, a igual costo, salga primero el que entró antes.
    desempate = 0
    frontera = [(0, desempate, problema.estado_inicial())]

    while frontera:
        if explorados >= max_nodos:
            motivo = MOTIVO_LIMITE
            break

        costo, _, estado = heapq.heappop(frontera)   # el de menor costo
        explorados += 1

        if problema.es_meta(estado):
            solucion = estado
            motivo = MOTIVO_ENCONTRADA
            break

        for hijo, costo_paso in problema.sucesores(estado):
            desempate += 1
            heapq.heappush(frontera, (costo + costo_paso, desempate, hijo))
            generados += 1

    if motivo == "":
        motivo = MOTIVO_SIN_SOLUCION

    return _crear_resultado("Costo uniforme", problema, solucion,
                            explorados, generados, inicio, motivo)


# ----------------------------------------------------------------------
# 3. Búsqueda en profundidad iterativa (IDS)
# ----------------------------------------------------------------------

class _LimiteExcedido(Exception):
    """Se usa para cortar la búsqueda cuando se pasa de max_nodos."""
    pass


class _BusquedaLimitada:
    """Búsqueda en profundidad con un límite de profundidad (DLS).
    Se guarda en una clase para poder llevar la cuenta de nodos entre todas
    las iteraciones de la búsqueda iterativa."""

    def __init__(self, problema, max_nodos):
        self.problema = problema
        self.max_nodos = max_nodos
        self.explorados = 0
        self.generados = 1

    def visitar(self, estado, limite):
        """Explora 'estado' en profundidad, bajando como máximo 'limite'
        niveles más. Devuelve el estado meta o None si no lo encuentra."""
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
    """Repite una búsqueda en profundidad aumentando el límite de profundidad
    0, 1, 2, ... hasta encontrar la meta. Combina lo bueno de BFS (encuentra la
    meta de menor profundidad) con el poco uso de memoria de la búsqueda en
    profundidad (solo guarda el camino actual).

    El límite máximo es el número de clases: más profundo que eso no existe.
    """
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
# Catálogo para la interfaz: nombre que se muestra -> función
# ----------------------------------------------------------------------

ALGORITMOS_NO_INFORMADOS = {
    "BFS (amplitud)": busqueda_amplitud,
    "Costo uniforme": busqueda_costo_uniforme,
    "Profundidad iterativa": busqueda_profundidad_iterativa,
}
