"""
estadisticas.py
===============
Resultado de una ejecución y tabla comparativa entre algoritmos.

  Resultado    -> lo que devuelve cada algoritmo al terminar (solución,
                  nodos explorados, tiempo...).
  Estadisticas -> guarda el último Resultado de cada algoritmo y entrega las
                  filas para el panel de estadísticas.
"""


class Resultado:
    """Resumen de una ejecución de un algoritmo de búsqueda.

    Atributos:
      algoritmo         nombre del algoritmo
      estado            Estado solución (None si no encontró)
      nodos_explorados  nodos sacados de la frontera y examinados
      nodos_generados   nodos creados al expandir (hijos generados)
      tiempo            segundos que tardó
      penalizacion      suma de penalizaciones blandas de la solución
      costo             costo total de la solución (clases + penalizaciones)
      motivo            texto explicando cómo terminó la búsqueda
    """

    def __init__(self, algoritmo, estado, nodos_explorados, nodos_generados,
                 tiempo, motivo, penalizacion=0, costo=0):
        self.algoritmo = algoritmo
        self.estado = estado
        self.nodos_explorados = nodos_explorados
        self.nodos_generados = nodos_generados
        self.tiempo = tiempo
        self.motivo = motivo
        self.penalizacion = penalizacion
        self.costo = costo

    @property
    def encontro(self):
        """True si la búsqueda encontró un horario completo."""
        return self.estado is not None

    def texto_solucion(self):
        return "Si" if self.encontro else "No"

    def texto_tiempo(self):
        return f"{self.tiempo:.3f}s"


class Estadisticas:
    """Tabla comparativa: una fila por algoritmo.

    Si se vuelve a correr un algoritmo, su fila se reemplaza por el resultado
    más reciente. Si se cambian los archivos de entrada conviene llamar a
    limpiar() para no comparar resultados de datos distintos.
    """

    ENCABEZADOS = ("Algoritmo", "Nodos", "Tiempo", "Solucion")

    def __init__(self):
        self._resultados = {}  # nombre del algoritmo -> Resultado

    def agregar(self, resultado):
        self._resultados[resultado.algoritmo] = resultado

    def limpiar(self):
        self._resultados.clear()

    def resultados(self):
        """Lista de Resultado, en el orden en que se corrió cada algoritmo
        por primera vez."""
        return list(self._resultados.values())

    def filas(self):
        """Filas listas para mostrar en la tabla:
        [(algoritmo, nodos, tiempo, solucion), ...]"""
        return [(r.algoritmo, r.nodos_explorados, r.texto_tiempo(), r.texto_solucion())
                for r in self._resultados.values()]

    def como_texto(self):
        """Tabla en texto plano (útil para probar desde consola)."""
        filas = [self.ENCABEZADOS] + [tuple(str(x) for x in f) for f in self.filas()]
        anchos = [max(len(f[i]) for f in filas) for i in range(len(self.ENCABEZADOS))]
        lineas = []
        for fila in filas:
            lineas.append("  ".join(campo.ljust(anchos[i]) for i, campo in enumerate(fila)))
        return "\n".join(lineas)
