import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from lector import (leer_profesores, leer_cursos, leer_salones, leer_franjas,
                    cargar_datos, ErrorLectura)
from modelo import dias_de, horas_de
from problema import ProblemaHorarios
from busqueda_no_informada import ALGORITMOS_NO_INFORMADOS
from a_asterisco import ALGORITMOS_INFORMADOS
from estadisticas import Estadisticas

# (clave interna, nombre que se ve, función que lee ese archivo)
ARCHIVOS = [
    ("profesores", "profesores.txt", leer_profesores),
    ("cursos", "cursos.txt", leer_cursos),
    ("salones", "salones.txt", leer_salones),
    ("franjas", "franjas.txt", leer_franjas),
]

# Todos los algoritmos juntos: nombre que se muestra -> función
ALGORITMOS = {**ALGORITMOS_NO_INFORMADOS, **ALGORITMOS_INFORMADOS}

COLOR_OK = "#2e7d32"
COLOR_ERROR = "#c62828"
COLOR_LIBRE = "#f2f2f2"
COLOR_OCUPADA = "#fff3cd"


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Programación académica universitaria")

        self.rutas = {}                  # clave -> ruta del archivo válido
        self.estadisticas = Estadisticas()

        self._construir_carga()
        self._construir_control()
        self._construir_horario()
        self._construir_estadisticas()

    # ------------------------------------------------------------------
    # Panel de carga de archivos
    # ------------------------------------------------------------------
    def _construir_carga(self):
        marco = ttk.LabelFrame(self, text="Archivos de entrada")
        marco.pack(fill="x", padx=10, pady=5)

        self.lbl_ruta = {}
        self.lbl_estado = {}

        for fila, (clave, nombre, _) in enumerate(ARCHIVOS):
            ttk.Label(marco, text=nombre, width=14).grid(
                row=fila, column=0, sticky="w", padx=5, pady=2)
            ttk.Button(marco, text="Examinar",
                       command=lambda c=clave: self._examinar(c)).grid(
                row=fila, column=1, padx=5)
            self.lbl_ruta[clave] = ttk.Label(marco, text="(sin cargar)",
                                             width=45, foreground="gray")
            self.lbl_ruta[clave].grid(row=fila, column=2, sticky="w", padx=5)
            self.lbl_estado[clave] = ttk.Label(marco, text="")
            self.lbl_estado[clave].grid(row=fila, column=3, padx=5)

    def _examinar(self, clave):
        # Buscamos la función que lee este archivo
        lector = next(fn for c, _, fn in ARCHIVOS if c == clave)
        ruta = filedialog.askopenfilename(
            title="Elegir archivo", filetypes=[("Archivos de texto", "*.txt")])
        if not ruta:
            return

        try:
            lector(ruta)                 # solo para validar el archivo
        except ErrorLectura as e:
            self.rutas.pop(clave, None)
            self._marcar(clave, ruta, leido=False)
            messagebox.showerror("Error al leer el archivo", str(e))
            return

        self.rutas[clave] = ruta
        self._marcar(clave, ruta, leido=True)

    def _marcar(self, clave, ruta, leido):
        self.lbl_ruta[clave].config(text=ruta, foreground="black")
        if leido:
            self.lbl_estado[clave].config(text="Leído", foreground=COLOR_OK)
        else:
            self.lbl_estado[clave].config(text="Error", foreground=COLOR_ERROR)

    # ------------------------------------------------------------------
    # Algoritmo y botón
    # ------------------------------------------------------------------
    def _construir_control(self):
        marco = ttk.Frame(self)
        marco.pack(fill="x", padx=10, pady=5)

        ttk.Label(marco, text="Algoritmo:").pack(side="left")
        self.combo = ttk.Combobox(marco, values=list(ALGORITMOS),
                                  state="readonly", width=24)
        self.combo.current(0)
        self.combo.pack(side="left", padx=5)

        ttk.Button(marco, text="Generar Horario",
                   command=self._generar).pack(side="left", padx=5)

        self.lbl_mensaje = ttk.Label(marco, text="")
        self.lbl_mensaje.pack(side="left", padx=10)

    def _generar(self):
        faltan = [nombre for clave, nombre, _ in ARCHIVOS
                  if clave not in self.rutas]
        if faltan:
            messagebox.showwarning("Faltan archivos",
                                   "Falta cargar: " + ", ".join(faltan))
            return

        try:
            _, cursos, salones, franjas = cargar_datos(
                self.rutas["profesores"], self.rutas["cursos"],
                self.rutas["salones"], self.rutas["franjas"])
        except ErrorLectura as e:
            messagebox.showerror("Error en los datos", str(e))
            return

        nombre = self.combo.get()
        problema = ProblemaHorarios(cursos, salones, franjas)

        # Mientras corre el algoritmo, el cursor cambia a reloj
        self.config(cursor="watch")
        self.update_idletasks()
        resultado = ALGORITMOS[nombre](problema)
        self.config(cursor="")

        self.estadisticas.agregar(resultado)
        self._mostrar_horario(resultado.estado, franjas)
        self._mostrar_estadisticas()

        if resultado.encontro:
            self.lbl_mensaje.config(
                text=f"{nombre}: costo {resultado.costo} (penalización {resultado.penalizacion})")
        else:
            self.lbl_mensaje.config(text=f"{nombre}: {resultado.motivo}")

    # ------------------------------------------------------------------
    # Grilla del horario
    # ------------------------------------------------------------------
    def _construir_horario(self):
        marco = ttk.LabelFrame(self, text="Horario")
        marco.pack(fill="both", expand=True, padx=10, pady=5)
        self.grilla = tk.Frame(marco)
        self.grilla.pack(padx=5, pady=5)

    def _mostrar_horario(self, estado, franjas):
        # Se borra la grilla anterior antes de dibujar la nueva
        for widget in self.grilla.winfo_children():
            widget.destroy()
        if not franjas:
            return

        dias = dias_de(franjas)     # columnas
        horas = horas_de(franjas)   # filas
        ocupadas = estado.a_grilla() if estado is not None else {}

        tk.Label(self.grilla, text="Hora", width=10, relief="ridge",
                 font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="nsew")
        for j, dia in enumerate(dias):
            tk.Label(self.grilla, text=dia, width=30, relief="ridge",
                     font=("Segoe UI", 9, "bold")).grid(row=0, column=j + 1, sticky="nsew")

        for i, hora in enumerate(horas):
            tk.Label(self.grilla, text=hora, width=10, relief="ridge").grid(
                row=i + 1, column=0, sticky="nsew")
            for j, dia in enumerate(dias):
                clases = ocupadas.get((dia, hora), [])
                if clases:
                    texto = "\n\n".join(
                        f"{a.curso.materia}\n{a.curso.profesor.nombre}\n{a.salon.nombre}"
                        for a in clases)
                    fondo = COLOR_OCUPADA
                else:
                    texto = ""
                    fondo = COLOR_LIBRE
                tk.Label(self.grilla, text=texto, width=30, bg=fondo,
                         relief="ridge", justify="center").grid(
                    row=i + 1, column=j + 1, sticky="nsew")

    # ------------------------------------------------------------------
    # Tabla de estadísticas
    # ------------------------------------------------------------------
    def _construir_estadisticas(self):
        marco = ttk.LabelFrame(self, text="Estadísticas")
        marco.pack(fill="x", padx=10, pady=5)

        self.tabla = ttk.Treeview(marco, columns=Estadisticas.ENCABEZADOS,
                                  show="headings", height=4)
        for col in Estadisticas.ENCABEZADOS:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center", width=140)
        self.tabla.pack(fill="x", padx=5, pady=5)

    def _mostrar_estadisticas(self):
        self.tabla.delete(*self.tabla.get_children())
        for fila in self.estadisticas.filas():
            self.tabla.insert("", "end", values=fila)