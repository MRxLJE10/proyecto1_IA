"""
problema.py
===========
Elementos del problema de búsqueda:
  - Estado inicial : ninguna clase asignada.
  - Sucesores      : tomar la SIGUIENTE clase (según el orden de cursos.txt)
                     y probar cada combinación (franja, salón) que cumpla las
                     restricciones duras.
  - Costo de paso  : 1 + penalizaciones blandas de esa asignación.
  - Meta           : todas las clases asignadas.

Espacio de búsqueda: es un árbol de profundidad N (N = número de clases).
En la raíz hay hasta (franjas x salones) hijos, cada nivel decide una clase.
"""

from modelo import Estado, Asignacion
from restricciones import (cumple_restricciones_duras, penalizacion_blanda,
                           MAX_CONSECUTIVAS)

# Costo mínimo de asignar una clase (sin penalizaciones). Útil para heurísticas:
# cada clase que falta por asignar cuesta al menos este valor.
COSTO_BASE = 1


class ProblemaHorarios:

    def __init__(self, cursos, salones, franjas, max_consecutivas=MAX_CONSECUTIVAS):
        for c in cursos:
            if c.profesor is None:
                raise ValueError(
                    f"El curso '{c.id}' no tiene profesor enlazado. "
                    f"Llame primero a lector.enlazar_datos()."
                )
        self.cursos = cursos
        self.salones = salones
        self.franjas = franjas
        self.max_consecutivas = max_consecutivas

    def estado_inicial(self):
        """Estado sin ninguna clase asignada."""
        return Estado()

    def es_meta(self, estado):
        """Meta: todas las clases tienen asignación. Como solo se agregan
        asignaciones que cumplen las restricciones duras, un estado completo
        ya es un horario válido."""
        return len(estado) == len(self.cursos)

    def curso_siguiente(self, estado):
        """Próxima clase por asignar (None si ya están todas)."""
        if len(estado) >= len(self.cursos):
            return None
        return self.cursos[len(estado)]

    def clases_restantes(self, estado):
        """Cuántas clases faltan por asignar."""
        return len(self.cursos) - len(estado)

    def sucesores(self, estado):
        """Lista de (nuevo_estado, costo_de_paso) para el estado dado.

        Se prueba cada combinación (franja, salón) para la siguiente clase y
        solo se conservan las que no violan ninguna restricción dura.
        """
        curso = self.curso_siguiente(estado)
        if curso is None:
            return []

        resultado = []
        for franja in self.franjas:
            for salon in self.salones:
                asignacion = Asignacion(curso, franja, salon)
                if cumple_restricciones_duras(estado, asignacion):
                    costo = COSTO_BASE + penalizacion_blanda(estado, asignacion,
                                                             self.max_consecutivas)
                    resultado.append((estado.agregar(asignacion), costo))
        return resultado

    def penalizacion_total(self, estado):
        """Suma de penalizaciones blandas de un estado (0 = cumple todas las
        restricciones blandas)."""
        total = 0
        parcial = Estado()
        for a in estado.asignaciones:
            total += penalizacion_blanda(parcial, a, self.max_consecutivas)
            parcial = parcial.agregar(a)
        return total

    def costo_total(self, estado):
        """Costo acumulado del estado: una unidad por clase asignada más las
        penalizaciones blandas."""
        return COSTO_BASE * len(estado) + self.penalizacion_total(estado)
