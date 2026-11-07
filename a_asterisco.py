"""
a_asterisco.py
==============
Búsqueda A* sobre ProblemaHorarios.

f(n) = g(n) + h(n)
  g(n): costo real acumulado desde el inicio hasta n
  h(n): cota inferior del costo que falta para llegar a una meta
"""

import time

from problema import COSTO_BASE
from restricciones import PESO_NO_DISPONIBLE
from estadisticas import Resultado
from cola_prioridad import ColaPrioridad
from busqueda_no_informada import (MAX_NODOS_DEFECTO, MOTIVO_ENCONTRADA,
                                   MOTIVO_LIMITE, MOTIVO_SIN_SOLUCION)


def preparar_heuristica(problema):
    minimos = []
    for curso in problema.cursos:
        hay_franja_libre = any(f.id not in curso.profesor.no_disponible
                               for f in problema.franjas)
        minimos.append(0 if hay_franja_libre else PESO_NO_DISPONIBLE)

    n = len(problema.cursos)
    sufijos = [0] * (n + 1)          # sufijos[n] = 0: no quedan clases
    for k in range(n - 1, -1, -1):
        sufijos[k] = sufijos[k + 1] + COSTO_BASE + minimos[k]
    return sufijos


def heuristica(sufijos, estado):
    """Cota inferior del costo restante. Admisible y consistente."""
    return sufijos[len(estado)]


def _crear_resultado(problema, solucion, explorados, generados, inicio, motivo):
    """Arma el Resultado final con el mismo formato que las demás búsquedas."""
    tiempo = time.perf_counter() - inicio
    penalizacion = 0
    costo = 0
    if solucion is not None:
        penalizacion = problema.penalizacion_total(solucion)
        costo = problema.costo_total(solucion)
    return Resultado("A*", solucion, explorados, generados, tiempo,
                     motivo, penalizacion, costo)


def a_asterisco(problema, max_nodos=MAX_NODOS_DEFECTO):
    """Busca el horario de menor costo usando f = g + h.
    Devuelve un Resultado. Si se supera max_nodos, el motivo lo indica.
    """
    inicio = time.perf_counter()
    explorados = 0
    generados = 1
    solucion = None
    motivo = ""

    sufijos = preparar_heuristica(problema)   # se calcula una sola vez
    estado0 = problema.estado_inicial()
    frontera = ColaPrioridad()
    # Cada elemento de la frontera es (g, estado); la prioridad es f = g + h
    frontera.agregar(heuristica(sufijos, estado0), (0, estado0))

    while len(frontera) > 0:
        if explorados >= max_nodos:
            motivo = MOTIVO_LIMITE
            break

        g, estado = frontera.extraer_minimo()
        explorados += 1

        # La meta se verifica al extraer, no al generar: así la solución
        # encontrada es la de menor costo.
        if problema.es_meta(estado):
            solucion = estado
            motivo = MOTIVO_ENCONTRADA
            break

        for hijo, costo_paso in problema.sucesores(estado):
            g_hijo = g + costo_paso
            f_hijo = g_hijo + heuristica(sufijos, hijo)
            frontera.agregar(f_hijo, (g_hijo, hijo))
            generados += 1

    if motivo == "":
        motivo = MOTIVO_SIN_SOLUCION

    return _crear_resultado(problema, solucion, explorados, generados,
                            inicio, motivo)


ALGORITMOS_INFORMADOS = {
    "A*": a_asterisco,
}