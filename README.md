# Asignación de horarios universitarios

Programa que genera un horario académico asignando a cada clase una franja horaria y un salón, sin conflictos de profesor, salón o grupo. Se implementan cuatro búsquedas (BFS, costo uniforme, profundidad iterativa y A*) y una interfaz gráfica con Tkinter.

## Cómo ejecutar

```
python main.py      # abre la interfaz gráfica
python pruebas.py   # corre las pruebas automáticas
```

Requiere solo la biblioteca estándar de Python (incluye `tkinter`).

## Archivos

| Archivo | Qué hace |
|---|---|
| `main.py` | Punto de entrada: abre la ventana. |
| `gui.py` | Interfaz: carga de archivos, selección de algoritmo, grilla del horario y tabla de estadísticas. |
| `modelo.py` | Clases `Profesor`, `Salon`, `Franja`, `Curso`, `Asignacion` y `Estado` (inmutable). |
| `lector.py` | Lee y valida los 4 `.txt`. `ErrorLectura` trae mensajes listos para mostrar. |
| `restricciones.py` | Restricciones duras (conflictos) y blandas (penalizaciones). |
| `problema.py` | `ProblemaHorarios`: estado inicial, sucesores, meta, costo y penalización. |
| `cola_prioridad.py` | Cola de prioridad (min-heap) implementada desde cero. La usan UCS y A*. |
| `busqueda_no_informada.py` | BFS, costo uniforme y profundidad iterativa. |
| `a_asterisco.py` | A* y la heurística `preparar_heuristica` / `heuristica`. |
| `estadisticas.py` | `Resultado` de cada ejecución y tabla comparativa `Estadisticas`. |
| `pruebas.py` | Pruebas automáticas de lectura, restricciones, algoritmos y heurística. |
| `datos/` | Ejemplo con solución. |
| `datos_penalizacion/` | Ejemplo con solución donde un profesor no tiene franjas disponibles. Muestra la ventaja de A* sobre UCS. |
| `datos_sin_solucion/` | Ejemplo sin solución. |

## Uso de la interfaz

1. Presionar **Examinar** en cada uno de los cuatro archivos y elegir el `.txt` correspondiente. Cada fila muestra "Leído" o "Error" con el motivo.
2. Elegir el algoritmo en el desplegable.
3. Presionar **Generar Horario**. La grilla muestra el horario, la tabla compara los algoritmos ejecutados y el mensaje junto al botón indica el costo y la penalización de la solución.

Si se cambia de algoritmo, hay que volver a presionar **Generar Horario** para que la grilla se actualice.

## Formato de los .txt

Las líneas vacías y las que empiezan con `#` se ignoran. Los campos van separados por coma.

```
profesores.txt   id,nombre[,franjas_no_disponibles]   P1,Prof_A,F1;F2
cursos.txt       id,materia,id_profesor,grupo         C1,Calculo,P1,G1
salones.txt      id,nombre                            S1,Salon_101
franjas.txt      id,dia,hora                          F1,Lunes,07-09
```

El orden de `franjas.txt` define el orden de las columnas (días) y filas (horas) de la grilla, y qué franjas son consecutivas. Conviene escribirlo en orden cronológico.

## Representación del estado

Las clases se asignan siempre en el orden de `cursos.txt`. Un estado es la lista de asignaciones de las primeras *k* clases. Por eso cada estado se alcanza por un único camino (no hay repetidos) y la meta es tener las *N* clases asignadas.

## Espacio de búsqueda

Árbol de profundidad *N*. Cada nivel decide una clase, y sus hijos son las combinaciones (franja, salón) que cumplen las restricciones duras.

**Costo de paso** = `COSTO_BASE` (1) + penalizaciones blandas de esa asignación.

**Costo de una solución** = una unidad por clase + penalización total.

**Penalización de una solución** = suma de las penalizaciones blandas de todas sus asignaciones.

## Restricciones

- **Duras** (se filtran al generar sucesores): un salón, un profesor o un grupo no pueden repetirse en una franja; cada clase se asigna una sola vez.
- **Blandas** (suman penalización):
  - Profesor en franja no disponible: **+5** (`PESO_NO_DISPONIBLE`).
  - Grupo con más de `MAX_CONSECUTIVAS` (3) clases seguidas en un día: **+3** por cada clase de exceso (`PESO_CONSECUTIVAS`).

## Algoritmos

- **BFS (amplitud):** cola FIFO. Encuentra una solución válida, pero ignora las penalizaciones, así que puede no ser la de menor costo.
- **Costo uniforme (UCS):** cola de prioridad por costo acumulado *g*. Encuentra el horario de menor costo (óptimo).
- **Profundidad iterativa (IDS):** búsqueda en profundidad con límite 0, 1, 2… hasta encontrar la meta.
- **A\*:** cola de prioridad por *f = g + h*. Encuentra el mismo horario óptimo que UCS, explorando menos nodos cuando la heurística aporta información.

Todos aceptan `max_nodos` (por defecto 100000). Si se supera, el `Resultado.motivo` lo indica.

## Heurística de A*

Para cada curso se calcula la penalización mínima que podría tener:
- **0** si su profesor tiene al menos una franja disponible.
- **5** si todas sus franjas están marcadas como no disponibles.

Entonces `h(estado)` es la suma de `COSTO_BASE + mínimo` para las clases que faltan. Se precalcula una tabla de sufijos, así que cada evaluación es constante.

- **Admisible:** nunca sobrestima, porque cada clase cuesta al menos `COSTO_BASE` y su penalización mínima se calcula sobre todas las franjas posibles.
- **Consistente:** el mínimo de cada curso no depende del estado, así que al expandir un nodo *h* baja exactamente lo que el paso cuesta como mínimo.
- **Limitación:** no estima las penalizaciones de consecutivas, porque dependen de cómo se combinan las clases de un mismo grupo.

Con `datos/` la heurística vale lo mismo que la de costo mínimo y A* explora los mismos nodos que UCS. Con `datos_penalizacion/` sí reduce la búsqueda.

## Resultados de referencia

| Carpeta | Algoritmo | Costo | Nodos explorados |
|---|---|---|---|
| `datos/` | UCS | 4 | 152 |
| `datos/` | A* | 4 | 152 |
| `datos/` | BFS | 9 (penalización 5) | 298 |
| `datos/` | IDS | 9 (penalización 5) | 369 |
| `datos_penalizacion/` | UCS | 9 | 178 |
| `datos_penalizacion/` | A* | 9 | 152 |
| `datos_penalizacion/` | BFS | 14 (penalización 10) | 298 |
| `datos_penalizacion/` | IDS | 14 (penalización 10) | 369 |
| `datos_sin_solucion/` | todos | sin solución | — |

UCS y A* siempre encuentran el horario óptimo. BFS e IDS encuentran una solución válida, pero no consideran las penalizaciones, por eso su costo es mayor. A* reduce los nodos explorados frente a UCS solo en `datos_penalizacion/`, donde la heurística ya conoce la penalización mínima de Prof_B.

Los tiempos varían en cada ejecución, así que no se incluyen en esta tabla.

## Uso desde otro módulo

```python
from lector import cargar_datos, ErrorLectura
from problema import ProblemaHorarios
from busqueda_no_informada import ALGORITMOS_NO_INFORMADOS
from a_asterisco import ALGORITMOS_INFORMADOS
from estadisticas import Estadisticas

profesores, cursos, salones, franjas = cargar_datos(rp, rc, rs, rf)   # puede lanzar ErrorLectura
problema = ProblemaHorarios(cursos, salones, franjas)

resultado = ALGORITMOS_INFORMADOS["A*"](problema)
# o: ALGORITMOS_NO_INFORMADOS["Costo uniforme"](problema)

resultado.encontro            # True / False
resultado.estado.a_grilla()   # {(dia, hora): [Asignacion, ...]}
resultado.costo, resultado.penalizacion
resultado.nodos_explorados, resultado.texto_tiempo(), resultado.texto_solucion()

estadisticas = Estadisticas()
estadisticas.agregar(resultado)
estadisticas.filas()          # [(algoritmo, nodos, tiempo, "Si"/"No"), ...]
```



