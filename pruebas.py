"""
pruebas.py
==========
Pruebas automáticas de lectura, restricciones, algoritmos y estadísticas.
Se ejecuta con:   python pruebas.py
Si todo está bien imprime "TODAS LAS PRUEBAS PASARON".
"""

import os
import tempfile

from modelo import Estado, Asignacion, Curso, Profesor, Salon, Franja
from lector import (ErrorLectura, cargar_datos, leer_franjas, leer_cursos,
                    leer_profesores, enlazar_datos)
from restricciones import (cumple_restricciones_duras, es_solucion_valida,
                           penalizacion_consecutivas, _exceso_consecutivas)
from problema import ProblemaHorarios
from busqueda_no_informada import (busqueda_amplitud, busqueda_costo_uniforme,
                                   busqueda_profundidad_iterativa,
                                   ALGORITMOS_NO_INFORMADOS)
from cola_prioridad import ColaFIFO
from a_asterisco import a_asterisco, preparar_heuristica, heuristica
from estadisticas import Estadisticas

CARPETA = os.path.dirname(os.path.abspath(__file__))


def ruta(*partes):
    return os.path.join(CARPETA, *partes)


def cargar_carpeta(nombre):
    return cargar_datos(ruta(nombre, "profesores.txt"), ruta(nombre, "cursos.txt"),
                        ruta(nombre, "salones.txt"), ruta(nombre, "franjas.txt"))


def esperar_error(funcion, *args):
    """Verifica que la función lance ErrorLectura."""
    try:
        funcion(*args)
    except ErrorLectura:
        return
    raise AssertionError("Se esperaba un ErrorLectura y no se lanzó")


def archivo_temporal(contenido):
    f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    f.write(contenido)
    f.close()
    return f.name


# ----------------------------------------------------------------------

def prueba_lectura_correcta():
    profesores, cursos, salones, franjas = cargar_carpeta("datos")
    assert len(profesores) == 3 and len(cursos) == 4
    assert len(salones) == 2 and len(franjas) == 4
    assert cursos[0].profesor.nombre == "Prof_A"          # enlazado
    assert profesores[0].no_disponible == {"F1"}
    # posición dentro del día: F1 y F3 son las primeras de su día
    assert [f.posicion for f in franjas] == [0, 1, 0, 1]


def prueba_lectura_errores():
    esperar_error(leer_franjas, ruta("no_existe.txt"))
    esperar_error(leer_franjas, archivo_temporal("F1,Lunes\n"))                  # faltan campos
    esperar_error(leer_franjas, archivo_temporal("F1,Lunes,07-09\nF1,Martes,07-09\n"))  # id repetido
    esperar_error(leer_franjas, archivo_temporal("F1,Lunes,07-09\nF2,Lunes,07-09\n"))   # franja repetida
    esperar_error(leer_franjas, archivo_temporal("# solo comentarios\n\n"))      # vacío
    # referencias que no existen
    cursos = leer_cursos(archivo_temporal("C1,Calculo,PX,G1\n"))
    esperar_error(enlazar_datos, leer_profesores(ruta("datos", "profesores.txt")),
                  cursos, [Salon("S1", "S")], [Franja("F1", "Lunes", "07-09")])
    profes = leer_profesores(archivo_temporal("P1,Prof_A,F9\n"))
    cursos = leer_cursos(archivo_temporal("C1,Calculo,P1,G1\n"))
    esperar_error(enlazar_datos, profes, cursos, [Salon("S1", "S")],
                  [Franja("F1", "Lunes", "07-09")])


def prueba_restricciones_duras():
    p1, p2 = Profesor("P1", "A"), Profesor("P2", "B")
    c1, c2, c3 = Curso("C1", "X", "P1", "G1"), Curso("C2", "Y", "P1", "G2"), Curso("C3", "Z", "P2", "G1")
    for c, p in ((c1, p1), (c2, p1), (c3, p2)):
        c.profesor = p
    f1, f2 = Franja("F1", "Lunes", "07-09"), Franja("F2", "Lunes", "09-11")
    s1, s2 = Salon("S1", "101"), Salon("S2", "102")

    e = Estado().agregar(Asignacion(c1, f1, s1))
    assert not cumple_restricciones_duras(e, Asignacion(c3, f1, s1))   # mismo salón
    assert not cumple_restricciones_duras(e, Asignacion(c2, f1, s2))   # mismo profesor
    assert not cumple_restricciones_duras(e, Asignacion(c3, f1, s2))   # mismo grupo
    assert not cumple_restricciones_duras(e, Asignacion(c1, f2, s1))   # curso repetido
    assert cumple_restricciones_duras(e, Asignacion(c3, f2, s1))       # todo bien


def prueba_restricciones_blandas():
    # Rachas de franjas seguidas con máximo 2
    assert _exceso_consecutivas([0, 1], 2) == 0
    assert _exceso_consecutivas([0, 1, 2], 2) == 1
    assert _exceso_consecutivas([0, 1, 2, 4], 2) == 1
    assert _exceso_consecutivas([0, 1, 3, 4], 2) == 0
    assert _exceso_consecutivas([0, 1, 3, 4, 2], 2) == 3   # una racha de 5
    # Penalización al agregar la tercera clase seguida
    profe = Profesor("P1", "A")
    franjas = [Franja(f"F{i}", "Lunes", f"h{i}", i) for i in range(3)]
    salon = Salon("S1", "101")
    estado = Estado()
    for i in range(2):
        c = Curso(f"C{i}", "M", "P1", "G1")
        c.profesor = profe
        estado = estado.agregar(Asignacion(c, franjas[i], salon))
    c = Curso("C9", "M", "P1", "G1")
    c.profesor = profe
    assert penalizacion_consecutivas(estado, Asignacion(c, franjas[2], salon), 2) > 0
    assert penalizacion_consecutivas(estado, Asignacion(c, franjas[2], salon), 3) == 0


def prueba_algoritmos_con_solucion():
    _, cursos, salones, franjas = cargar_carpeta("datos")
    problema = ProblemaHorarios(cursos, salones, franjas)
    resultados = {}
    for nombre, algoritmo in ALGORITMOS_NO_INFORMADOS.items():
        r = algoritmo(problema)
        assert r.encontro, nombre
        assert es_solucion_valida(r.estado, cursos), nombre
        assert r.nodos_explorados > 0 and r.tiempo >= 0
        resultados[nombre] = r
    # Costo uniforme debe ser óptimo: nunca peor que los otros
    ucs = resultados["Costo uniforme"]
    for r in resultados.values():
        assert ucs.costo <= r.costo
    assert ucs.penalizacion == 0       # en estos datos existe un horario sin penalización
    assert resultados["BFS (amplitud)"].costo >= ucs.costo


def prueba_a_asterisco():
    _, cursos, salones, franjas = cargar_carpeta("datos")
    problema = ProblemaHorarios(cursos, salones, franjas)
    ucs = busqueda_costo_uniforme(problema)
    astar = a_asterisco(problema)

    assert astar.encontro and es_solucion_valida(astar.estado, cursos)
    assert astar.costo == ucs.costo                        # mismo óptimo
    assert astar.nodos_explorados <= ucs.nodos_explorados  # nunca explora más

    sufijos = preparar_heuristica(problema)
    assert heuristica(sufijos, problema.estado_inicial()) <= ucs.costo  # admisible


def prueba_sin_solucion():
    _, cursos, salones, franjas = cargar_carpeta("datos_sin_solucion")
    problema = ProblemaHorarios(cursos, salones, franjas)
    for nombre, algoritmo in ALGORITMOS_NO_INFORMADOS.items():
        r = algoritmo(problema)
        assert not r.encontro and r.estado is None, nombre
        assert "No existe solución" in r.motivo, nombre


def prueba_limite_de_nodos():
    _, cursos, salones, franjas = cargar_carpeta("datos")
    problema = ProblemaHorarios(cursos, salones, franjas)
    for nombre, algoritmo in ALGORITMOS_NO_INFORMADOS.items():
        r = algoritmo(problema, max_nodos=5)
        assert not r.encontro, nombre
        assert r.nodos_explorados == 5, nombre
        assert "límite" in r.motivo, nombre


def prueba_estadisticas():
    _, cursos, salones, franjas = cargar_carpeta("datos")
    problema = ProblemaHorarios(cursos, salones, franjas)
    est = Estadisticas()
    est.agregar(busqueda_amplitud(problema))
    est.agregar(busqueda_costo_uniforme(problema))
    est.agregar(busqueda_profundidad_iterativa(problema))
    assert len(est.filas()) == 3
    est.agregar(busqueda_amplitud(problema))     # repetir reemplaza la fila
    assert len(est.filas()) == 3
    nombre, nodos, tiempo, solucion = est.filas()[0]
    assert solucion == "Si" and tiempo.endswith("s") and nodos > 0
    est.limpiar()
    assert est.filas() == []


def prueba_grilla():
    _, cursos, salones, franjas = cargar_carpeta("datos")
    r = busqueda_costo_uniforme(ProblemaHorarios(cursos, salones, franjas))
    grilla = r.estado.a_grilla()
    total = sum(len(lista) for lista in grilla.values())
    assert total == len(cursos)

def prueba_consistencia():
    _, cursos, salones, franjas = cargar_carpeta("datos")
    problema = ProblemaHorarios(cursos, salones, franjas)
    sufijos = preparar_heuristica(problema)
    pendientes = [problema.estado_inicial()]
    revisadas = 0
    while pendientes:
        padre = pendientes.pop()
        for hijo, costo in problema.sucesores(padre):
            revisadas += 1
            assert heuristica(sufijos, padre) <= costo + heuristica(sufijos, hijo)
            pendientes.append(hijo)
    assert revisadas > 0

def prueba_cola_fifo():
    f = ColaFIFO()
    for v in ["a", "b", "c"]:
        f.agregar(v)
    assert [f.extraer_primero() for _ in range(3)] == ["a", "b", "c"]
    try:
        f.extraer_primero()
        raise AssertionError("debía lanzar IndexError")
    except IndexError:
        pass


if __name__ == "__main__":
    pruebas = [prueba_lectura_correcta, prueba_lectura_errores,
               prueba_restricciones_duras, prueba_restricciones_blandas,
               prueba_algoritmos_con_solucion, prueba_a_asterisco,
               prueba_sin_solucion, prueba_limite_de_nodos,
               prueba_estadisticas, prueba_grilla, prueba_consistencia, prueba_cola_fifo]
    for prueba in pruebas:
        prueba()
        print(f"OK  {prueba.__name__}")
    print("\nTODAS LAS PRUEBAS PASARON")