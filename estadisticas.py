class Resultado:

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

    ENCABEZADOS = ("Algoritmo", "Nodos", "Tiempo", "Solucion")

    def __init__(self):
        self._resultados = {}  # nombre del algoritmo -> Resultado

    def agregar(self, resultado):
        self._resultados[resultado.algoritmo] = resultado

    def limpiar(self):
        self._resultados.clear()

    def resultados(self):
        return list(self._resultados.values())

    def filas(self):
        return [(r.algoritmo, r.nodos_explorados, r.texto_tiempo(), r.texto_solucion())
                for r in self._resultados.values()]

    def como_texto(self):
        filas = [self.ENCABEZADOS] + [tuple(str(x) for x in f) for f in self.filas()]
        anchos = [max(len(f[i]) for f in filas) for i in range(len(self.ENCABEZADOS))]
        lineas = []
        for fila in filas:
            lineas.append("  ".join(campo.ljust(anchos[i]) for i, campo in enumerate(fila)))
        return "\n".join(lineas)
