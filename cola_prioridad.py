class ColaPrioridad:

    def __init__(self):
        self._datos = []      # lista que representa el heap
        self._contador = 0    # cuántas inserciones se hicieron

    def __len__(self):
        return len(self._datos)

    def agregar(self, prioridad, valor):
        """Inserta un elemento al final del heap y lo sube a su lugar."""
        self._datos.append((prioridad, self._contador, valor))
        self._contador += 1
        self._subir(len(self._datos) - 1)

    def extraer_minimo(self):
        """Quita y devuelve el valor con menor prioridad."""
        if not self._datos:
            raise IndexError("La cola está vacía")
        raiz = self._datos[0]
        ultimo = self._datos.pop()        # último elemento del heap
        if self._datos:
            self._datos[0] = ultimo       # lo ponemos arriba
            self._bajar(0)                # y lo bajamos a su lugar
        return raiz[2]

    def _menor(self, i, j):
        """True si el elemento i va antes que el j: primero por prioridad,
        y si empatan, por orden de llegada."""
        pi, oi, _ = self._datos[i]
        pj, oj, _ = self._datos[j]
        return (pi, oi) < (pj, oj)

    def _intercambiar(self, i, j):
        self._datos[i], self._datos[j] = self._datos[j], self._datos[i]

    def _subir(self, i):
        """Sube el elemento i mientras sea menor que su padre."""
        while i > 0:
            padre = (i - 1) // 2
            if not self._menor(i, padre):
                break
            self._intercambiar(i, padre)
            i = padre

    def _bajar(self, i):
        """Baja el elemento i mientras algún hijo sea menor que él."""
        n = len(self._datos)
        while True:
            izq = 2 * i + 1
            der = 2 * i + 2
            menor = i
            if izq < n and self._menor(izq, menor):
                menor = izq
            if der < n and self._menor(der, menor):
                menor = der
            if menor == i:
                break
            self._intercambiar(i, menor)
            i = menor

class ColaFIFO:
    """Fila: el primero que entra es el primero que sale. """

    def __init__(self):
        self._datos = []
        self._inicio = 0

    def __len__(self):
        return len(self._datos) - self._inicio

    def agregar(self, valor):
        """Agrega al final de la fila."""
        self._datos.append(valor)

    def extraer_primero(self):
        """Quita y devuelve el elemento del frente."""
        if len(self) == 0:
            raise IndexError("La cola está vacía")
        valor = self._datos[self._inicio]
        self._datos[self._inicio] = None   # libera la referencia
        self._inicio += 1
        if self._inicio * 2 >= len(self._datos):
            self._datos = self._datos[self._inicio:]
            self._inicio = 0
        return valor