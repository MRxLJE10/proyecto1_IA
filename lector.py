"""
lector.py
=========
Lectura y validación de los 4 archivos .txt de entrada.

Formato general (una línea = un registro, campos separados por coma):
  - Las líneas vacías y las que empiezan por '#' se ignoran (comentarios).
  - Se pueden leer los archivos en cualquier orden; las referencias entre
    archivos (profesor de un curso, franjas no disponibles) se revisan
    después, en enlazar_datos().

    profesores.txt   id,nombre[,franjas_no_disponibles]    (ids separados por ;)
    cursos.txt       id,materia,id_profesor,grupo
    salones.txt      id,nombre
    franjas.txt      id,dia,hora

Cualquier problema (archivo inexistente, línea mal formada, ids repetidos,
referencias que no existen) lanza ErrorLectura con un mensaje que se puede
mostrar directamente al usuario en la interfaz.
"""

from modelo import Profesor, Curso, Salon, Franja


class ErrorLectura(Exception):
    """Error al leer o validar un archivo de entrada."""
    pass


def _leer_registros(ruta, nombre_archivo, min_campos, max_campos):
    """Lee un archivo y devuelve una lista de (numero_de_linea, [campos]).

    Se encarga de lo común a los 4 archivos: abrir, saltar comentarios y
    líneas vacías, separar por comas y verificar la cantidad de campos.
    """
    try:
        # utf-8-sig tolera el BOM que a veces agrega el Bloc de notas
        with open(ruta, encoding="utf-8-sig") as archivo:
            lineas = archivo.readlines()
    except FileNotFoundError:
        raise ErrorLectura(f"{nombre_archivo}: no se encontró el archivo '{ruta}'.")
    except UnicodeDecodeError:
        raise ErrorLectura(f"{nombre_archivo}: el archivo debe estar guardado en UTF-8.")
    except OSError as e:
        raise ErrorLectura(f"{nombre_archivo}: no se pudo abrir '{ruta}' ({e.strerror}).")

    registros = []
    for numero, linea in enumerate(lineas, start=1):
        linea = linea.strip()
        if linea == "" or linea.startswith("#"):
            continue
        campos = [c.strip() for c in linea.split(",")]
        if not (min_campos <= len(campos) <= max_campos):
            raise ErrorLectura(
                f"{nombre_archivo}, línea {numero}: se esperaban "
                f"{_texto_cantidad(min_campos, max_campos)} campos y hay {len(campos)}."
            )
        # Los campos obligatorios no pueden estar vacíos
        if "" in campos[:min_campos]:
            raise ErrorLectura(f"{nombre_archivo}, línea {numero}: hay un campo vacío.")
        registros.append((numero, campos))

    if not registros:
        raise ErrorLectura(f"{nombre_archivo}: el archivo no tiene datos.")
    return registros


def _texto_cantidad(minimo, maximo):
    return str(minimo) if minimo == maximo else f"{minimo} o {maximo}"


def _verificar_id_unico(ids_vistos, id, nombre_archivo, numero):
    if id in ids_vistos:
        raise ErrorLectura(f"{nombre_archivo}, línea {numero}: el id '{id}' está repetido.")
    ids_vistos.add(id)


# ----------------------------------------------------------------------
# Un lector por archivo
# ----------------------------------------------------------------------

def leer_franjas(ruta):
    """franjas.txt -> lista de Franja. Formato: id,dia,hora"""
    franjas = []
    ids = set()
    combinaciones = set()
    posicion_en_dia = {}  # dia -> cuántas franjas van en ese día

    for numero, (id, dia, hora) in _leer_registros(ruta, "franjas.txt", 3, 3):
        _verificar_id_unico(ids, id, "franjas.txt", numero)
        if (dia, hora) in combinaciones:
            raise ErrorLectura(f"franjas.txt, línea {numero}: la franja '{dia} {hora}' está repetida.")
        combinaciones.add((dia, hora))

        # La posición dentro del día sale del orden del archivo
        posicion = posicion_en_dia.get(dia, 0)
        posicion_en_dia[dia] = posicion + 1
        franjas.append(Franja(id, dia, hora, posicion))
    return franjas


def leer_salones(ruta):
    """salones.txt -> lista de Salon. Formato: id,nombre"""
    salones = []
    ids = set()
    for numero, (id, nombre) in _leer_registros(ruta, "salones.txt", 2, 2):
        _verificar_id_unico(ids, id, "salones.txt", numero)
        salones.append(Salon(id, nombre))
    return salones


def leer_profesores(ruta):
    """profesores.txt -> lista de Profesor.
    Formato: id,nombre[,franjas_no_disponibles]  (ej: P1,Prof_A,F1;F2)"""
    profesores = []
    ids = set()
    for numero, campos in _leer_registros(ruta, "profesores.txt", 2, 3):
        id, nombre = campos[0], campos[1]
        _verificar_id_unico(ids, id, "profesores.txt", numero)
        no_disponible = []
        if len(campos) == 3:
            no_disponible = [f.strip() for f in campos[2].split(";") if f.strip()]
        profesores.append(Profesor(id, nombre, no_disponible))
    return profesores


def leer_cursos(ruta):
    """cursos.txt -> lista de Curso. Formato: id,materia,id_profesor,grupo"""
    cursos = []
    ids = set()
    for numero, (id, materia, id_profesor, grupo) in _leer_registros(ruta, "cursos.txt", 4, 4):
        _verificar_id_unico(ids, id, "cursos.txt", numero)
        cursos.append(Curso(id, materia, id_profesor, grupo))
    return cursos


# ----------------------------------------------------------------------
# Validación cruzada entre archivos
# ----------------------------------------------------------------------

def enlazar_datos(profesores, cursos, salones, franjas):
    """Revisa que los 4 archivos sean coherentes entre sí y conecta cada
    Curso con su objeto Profesor (curso.profesor).

    Se debe llamar cuando ya se leyeron los 4 archivos y antes de crear el
    problema. Lanza ErrorLectura si algo no cuadra.
    """
    por_id = {p.id: p for p in profesores}
    for curso in cursos:
        if curso.id_profesor not in por_id:
            raise ErrorLectura(
                f"cursos.txt: el curso '{curso.id}' usa el profesor '{curso.id_profesor}', "
                f"que no existe en profesores.txt."
            )
        curso.profesor = por_id[curso.id_profesor]

    ids_franjas = {f.id for f in franjas}
    for profesor in profesores:
        for id_franja in profesor.no_disponible:
            if id_franja not in ids_franjas:
                raise ErrorLectura(
                    f"profesores.txt: el profesor '{profesor.id}' marca como no disponible "
                    f"la franja '{id_franja}', que no existe en franjas.txt."
                )


def cargar_datos(ruta_profesores, ruta_cursos, ruta_salones, ruta_franjas):
    """Atajo: lee los 4 archivos, los enlaza y devuelve
    (profesores, cursos, salones, franjas)."""
    profesores = leer_profesores(ruta_profesores)
    cursos = leer_cursos(ruta_cursos)
    salones = leer_salones(ruta_salones)
    franjas = leer_franjas(ruta_franjas)
    enlazar_datos(profesores, cursos, salones, franjas)
    return profesores, cursos, salones, franjas
