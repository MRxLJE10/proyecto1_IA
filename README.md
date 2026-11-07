# Asignación de horarios universitarios 


## Archivos

| Archivo | Qué hace |
|---|---|
| `modelo.py` | Clases `Profesor`, `Salon`, `Franja`, `Curso`, `Asignacion` y `Estado` (inmutable). |
| `lector.py` | Lee y valida los 4 `.txt`; `ErrorLectura` trae mensajes listos para mostrar. |
| `restricciones.py` | Restricciones duras (conflictos) y blandas (penalizaciones). |
| `problema.py` | `ProblemaHorarios`: estado inicial, sucesores, meta y costos. |
| `busqueda_no_informada.py` | BFS, costo uniforme y profundidad iterativa. |
| `estadisticas.py` | `Resultado` de cada ejecución y tabla comparativa `Estadisticas`. |
| `pruebas.py` | Pruebas automáticas: `python pruebas.py`. |
| `datos/` | Ejemplo con solución. |
| `datos_sin_solucion/` | Ejemplo sin solución (prueba el caso "No"). |

## Formato de los .txt
Líneas vacías y que empiezan con `#` se ignoran. Campos separados por coma.

```
profesores.txt   id,nombre[,franjas_no_disponibles]   P1,Prof_A,F1;F2
cursos.txt       id,materia,id_profesor,grupo         C1,Calculo,P1,G1
salones.txt      id,nombre                            S1,Salon_101
franjas.txt      id,dia,hora                          F1,Lunes,07-09
```
El orden de `franjas.txt` define el orden de columnas (días) y filas (horas) de la grilla, y qué franjas son consecutivas.

## Representación del estado
Las clases se asignan siempre en el orden de `cursos.txt`. Un estado es la lista de asignaciones de las primeras *k* clases. Por eso cada estado se alcanza por un único camino (no hay repetidos) y la meta es tener las *N* clases asignadas.

## Espacio de búsqueda
Árbol de profundidad *N*. Cada nivel decide una clase; sus hijos son las combinaciones (franja, salón) que cumplen las restricciones duras. Costo de paso = 1 + penalizaciones blandas.

## Restricciones
- **Duras** (se filtran al generar sucesores): salón, profesor y grupo no pueden repetirse en una franja; cada clase se asigna una vez.
- **Blandas** (suman costo): profesor en franja no disponible (+5); grupo con más de `MAX_CONSECUTIVAS` (3) clases seguidas en un día (+3 por clase de exceso).

## Algoritmos
- **BFS**: cola FIFO. Halla una solución válida, pero ignora las penalizaciones blandas.
- **Costo uniforme**: cola de prioridad por costo acumulado. Halla el horario de menor costo (óptimo).
- **Profundidad iterativa**: búsqueda en profundidad con límite 0, 1, 2… hasta la meta.

Todos aceptan `max_nodos` (por defecto 100000) para no quedarse pegados en datos grandes; si se supera, el `Resultado.motivo` lo indica.

## Uso desde otro módulo (interfaz / main)
```python
from lector import cargar_datos, ErrorLectura
from problema import ProblemaHorarios
from busqueda_no_informada import ALGORITMOS_NO_INFORMADOS
from estadisticas import Estadisticas

profesores, cursos, salones, franjas = cargar_datos(rp, rc, rs, rf)   # puede lanzar ErrorLectura
problema = ProblemaHorarios(cursos, salones, franjas)
resultado = ALGORITMOS_NO_INFORMADOS["Costo uniforme"](problema)

resultado.encontro            # True / False
resultado.estado.a_grilla()   # {(dia, hora): [Asignacion, ...]}
resultado.nodos_explorados, resultado.texto_tiempo(), resultado.texto_solucion()

estadisticas = Estadisticas()
estadisticas.agregar(resultado)
estadisticas.filas()          # [(algoritmo, nodos, tiempo, "Si"/"No"), ...]
```



