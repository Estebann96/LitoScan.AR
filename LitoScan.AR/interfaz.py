import sys
import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
import subprocess
from PIL import Image, ImageTk
import picamerax as picamera
import io
import time

# Nombre del archivo CSV
archivo_csv = "data/configuracion.csv"

# Nombre predeterminado que no se debe eliminar
config_predeterminada = "PiAutoStageAR"

# Función para verificar si la carpeta existe en el escritorio
def verificar_carpeta(carpeta):
    escritorio = os.path.expanduser("~/Desktop")
    ruta_carpeta = os.path.join(escritorio, carpeta)
    
    if os.path.exists(ruta_carpeta):
        return True
    else:
        os.makedirs(ruta_carpeta)
        return False

# Función que se ejecuta cuando se presiona el botón iniciar
def ejecutar_codigo():
    # Verifica si todos los campos están llenos
    campos = [
        entry_x_home, entry_y_home, entry_num_x, entry_num_y,
        entry_x_ini, entry_x_max, entry_y_ini, entry_y_max,
        entry_focus_pos, entry_isx, entry_res_x, entry_res_y, entry_carpeta
    ]
    
    for campo in campos:
        if not campo.get():
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return
    
    # Deshabilita botones
    boton_ejecutar.config(state=tk.DISABLED)
    boton_agregar.config(state=tk.DISABLED)
    boton_eliminar.config(state=tk.DISABLED)
    boton_importar.config(state=tk.DISABLED)
    boton_info.config(state=tk.DISABLED)
    # Cambia el estado de etiqueta
    etiqueta_estado.config(text="Ejecutando", bg="lightgreen")
    
    # Obtener los valores ingresados
    x_home = entry_x_home.get()
    y_home = entry_y_home.get()
    num_x = entry_num_x.get()
    num_y = entry_num_y.get()
    x_ini = entry_x_ini.get()
    x_max = entry_x_max.get()
    y_ini = entry_y_ini.get()
    y_max = entry_y_max.get()
    focus_pos = entry_focus_pos.get()
    isx = entry_isx.get()
    res_x = entry_res_x.get()
    res_y = entry_res_y.get()
    carpeta = entry_carpeta.get()

    # Verificar si la carpeta existe
    if verificar_carpeta(carpeta):
        messagebox.showerror("Error", "La carpeta ya existe. Ingrese otro nombre.")
        # Habilita botones
        boton_ejecutar.config(state=tk.NORMAL)
        boton_agregar.config(state=tk.NORMAL)
        boton_eliminar.config(state=tk.NORMAL)
        boton_importar.config(state=tk.NORMAL)
        boton_info.config(state=tk.NORMAL)
        # Cambia el estado de etiqueta
        etiqueta_estado.config(text="En espera", bg="lightgray")
        return
    else:
        messagebox.showinfo("Notificación", f"La carpeta '{carpeta}' ha sido creada exitosamente.")
        

    # Llamar al script principal.py con los parámetros
    try:
        subprocess.run(['python3', 'main.py', x_home, y_home, num_x, num_y, x_ini, x_max, y_ini, y_max, focus_pos, isx, res_x, res_y, carpeta])

    except Exception as e:
        etiqueta_estado.config(text="Error", bg="red")
        messagebox.showerror("Notificación", f"Error al ejecutar el código: {e}")
        
    # Habilita botones
    boton_ejecutar.config(state=tk.NORMAL)
    boton_agregar.config(state=tk.NORMAL)
    boton_eliminar.config(state=tk.NORMAL)
    boton_importar.config(state=tk.NORMAL)
    boton_info.config(state=tk.NORMAL)
    # Cambia el estado de etiqueta
    etiqueta_estado.config(text="En espera", bg="lightgray")



# Función crear el archivo CSV si no existe
def crear_csv_si_no_existe():
    if not os.path.exists(archivo_csv):
        with open(archivo_csv, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Nombre", "x_home", "y_home", "num_x", "num_y", "x_ini", "x_max", "y_ini", "y_max", "focus_pos", "isx", "res_x", "res_y"])

# Función leer datos del archivo CSV
def leer_csv():
    with open(archivo_csv, mode="r") as file:
        reader = csv.DictReader(file)
        return list(reader)

# Función escribir datos en el archivo CSV
def escribir_csv(data):
    with open(archivo_csv, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Nombre", "x_home", "y_home", "num_x", "num_y", "x_ini", "x_max", "y_ini", "y_max", "focus_pos", "isx", "res_x", "res_y"])
        writer.writerows(data)

# Función para refrescar la tabla de datos
def refrescar_tabla():
    for row in tree.get_children():
        tree.delete(row)

    for row in leer_csv():
        tree.insert("", tk.END, values=(row["Nombre"], row["x_home"], row["y_home"], row["num_x"], row["num_y"], row["x_ini"], row["x_max"], row["y_ini"], row["y_max"], row["focus_pos"], row["isx"], row["res_x"], row["res_y"]))


# Función que se ejecuta cuando se presiona el botón agregar configuración
def agregar_configuracion():
    nombre = entry_nombre.get()
    valores = [
        entry_x_home.get(), entry_y_home.get(), entry_num_x.get(), entry_num_y.get(),
        entry_x_ini.get(), entry_x_max.get(), entry_y_ini.get(), entry_y_max.get(),
        entry_focus_pos.get(), 
        entry_isx.get(), entry_res_x.get(), entry_res_y.get()
    ]

    if not nombre or any(not valor for valor in valores):
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return

    # Verificar si el nombre ya existe
    data = leer_csv()
    if any(row["Nombre"] == nombre for row in data):
        messagebox.showerror("Error", f"El nombre '{nombre}' ya existe. Por favor, elija otro nombre.")
        return

    try:
        # Convertir valores a los tipos correspondientes
        valores_convertidos = [
            float(val) if idx not in [9, 10, 11, 12, 13, 14, 15] else int(val)
            for idx, val in enumerate(valores)
        ]
    except ValueError:
        messagebox.showerror("Error", "Algunos valores no son válidos.")
        return

    with open(archivo_csv, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([nombre, *valores])

    messagebox.showinfo("Éxito", "Configuración agregada correctamente.")
    refrescar_tabla()
 


# Función que se ejecuta cuando se presiona el botón eliminar configuración
def eliminar_configuracion():
    item_seleccionado = tree.selection()

    if not item_seleccionado:
        messagebox.showerror("Error", "Por favor, seleccione una configuración para eliminar.")
        return

    datos_seleccionados = tree.item(item_seleccionado, "values")

    # Validar si el nombre de la configuración es el predeterminado
    if datos_seleccionados[0] == config_predeterminada:
        messagebox.showerror("Error", f"No se puede eliminar la configuración con nombre '{config_predeterminada}'.")
        return

    confirm = messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar la configuración seleccionada?")

    if not confirm:
        return

    data = leer_csv()
    nueva_data = [row for row in data if row["Nombre"] != datos_seleccionados[0]]

    escribir_csv([[row["Nombre"], row["x_home"], row["y_home"], row["num_x"], row["num_y"], row["x_ini"], row["x_max"], row["y_ini"], row["y_max"], row["focus_pos"], row["isx"], row["res_x"], row["res_y"]] for row in nueva_data])

    refrescar_tabla()
    messagebox.showinfo("Éxito", "Configuración eliminada correctamente.")

# Función que se ejecuta cuando se presiona el botón importar
def importar_configuracion():
    item_seleccionado = tree.selection()

    if not item_seleccionado:
        messagebox.showerror("Error", "Por favor, seleccione una fila para importar.")
        return

    # Obtener los datos de la fila seleccionada
    datos_seleccionados = tree.item(item_seleccionado, "values")

    # Rellenar los campos de entrada con los datos de la fila seleccionada
    entry_nombre.delete(0, tk.END)
    entry_nombre.insert(0, datos_seleccionados[0])

    entry_x_home.delete(0, tk.END)
    entry_x_home.insert(0, datos_seleccionados[1])

    entry_y_home.delete(0, tk.END)
    entry_y_home.insert(0, datos_seleccionados[2])

    entry_num_x.delete(0, tk.END)
    entry_num_x.insert(0, datos_seleccionados[3])

    entry_num_y.delete(0, tk.END)
    entry_num_y.insert(0, datos_seleccionados[4])

    entry_x_ini.delete(0, tk.END)
    entry_x_ini.insert(0, datos_seleccionados[5])

    entry_x_max.delete(0, tk.END)
    entry_x_max.insert(0, datos_seleccionados[6])

    entry_y_ini.delete(0, tk.END)
    entry_y_ini.insert(0, datos_seleccionados[7])

    entry_y_max.delete(0, tk.END)
    entry_y_max.insert(0, datos_seleccionados[8])

    entry_focus_pos.delete(0, tk.END)
    entry_focus_pos.insert(0, datos_seleccionados[9])

    entry_isx.delete(0, tk.END)
    entry_isx.insert(0, datos_seleccionados[10])

    entry_res_x.delete(0, tk.END)
    entry_res_x.insert(0, datos_seleccionados[11])

    entry_res_y.delete(0, tk.END)
    entry_res_y.insert(0, datos_seleccionados[12])


#Función que se ejecuta cuando se presiona el botón información
def show_info():
    info_window = tk.Toplevel(ventana)
    info_window.title("Información sobre LitoScan.AR")
    
    # Crear un marco para el encabezado
    frame_titulo = tk.Frame(info_window)
    frame_titulo.pack(pady=10)

    # Cargar y mostrar el logo
    logo = tk.PhotoImage(file="assets/logo.png")
    label_logo = tk.Label(frame_titulo, image=logo)
    label_logo.image = logo  
    label_logo.pack()

    # Título y subtítulo
    etiqueta_titulo = tk.Label(frame_titulo, text="LitoScan.AR - 2025", font=("Arial", 16, "bold"))
    etiqueta_titulo.pack()

    etiqueta_subtitulo = tk.Label(frame_titulo, text="Desarrollado por Esteban Martinez", font=("Arial", 12, "italic"))
    etiqueta_subtitulo.pack()

    info_text = """
    
    Es importante tener en cuenta que, para garantizar una correcta funcionalidad del programa, es necesario que todos los parámetros estén completos.

    A continuación, se detallan los parámetros del sistema LitoScan.AR:

    1. Posición inicial del sistema (x_home y y_home)
    Establecen las coordenadas de la posición inicial de la plataforma en el sistema.
    2. Número de pasos a lo largo de los ejes (num_x y num_y)
    Indican el número de pasos que el sistema de posicionamiento debe realizar en cada eje.
    3. Límites del escenario (x_ini, x_max, y_ini y i_max).
    Definen los limites físicos del área en la que el sistema de posicionamiento puede moverse.
    4. Posición de enfoque (focus_pos)
    Establece la posición de enfoque de la cámara en términos de coordenadas (X,Y). Por ejemplo, el valor 13001200 indica que el foco debe estar centrado en las coordenadas X=1300 y Y=1200.
    5. Valor de ISO de la cámara (isx)
    Indica el valor de ISO utilizado para la captura de imágenes.
    6. Resolución de captura de imágenes (rex_x, res_y)
    Ajustan la resolución de las imágenes capturadas.
    7. Nombre de la carpeta (carpeta)
    Hace referencia al nombre del directorio que se creará en el escritorio para guardar las capturas realizadas por el sistema.

    LitoScan.AR permite guardar las configuraciones de los parámetros definidos por el usuario para que puedan ser reutilizados en el futuro. Es crucial guardar estas configuraciones con un nombre
    claro, para facilitar su identificación. Es importante destacar que la configuración PiAutoStageAR es la configuración predeterminada (default).
    
    """
    
    etiqueta_info = tk.Label(info_window, text=info_text, justify="left", padx=10, pady=10,font=("Arial", 10))
    etiqueta_info.pack()
    
class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vista en Directo - Cámara Raspberry Pi")
        
        # Crear un widget de etiqueta para mostrar la imagen
        self.label = tk.Label(root)
        self.label.pack()
        
        with picamera.PiCamera() as camera:
            camera.resolution = (640, 480)
            camera.iso = int(entry_isx.get())
            camera.start_preview()
            time.sleep(3)
            q1 = camera.exposure_speed
            g = camera.awb_gains
            camera.stop_preview()
        
        q=q1
        g=g
        
        # Inicializar la cámara
        self.camera = picamera.PiCamera()
        self.camera.iso = int(entry_isx.get())
        self.camera.shutter_speed = q
        self.camera.exposure_mode = 'off'
        self.camera.awb_mode = 'off'
        self.camera.awb_gains = g
        self.camera.resolution = (640, 480)
        
        # Iniciar actualización de la imagen
        self.update_frame()
        
        # Botón para cerrar
        self.btn_exit = tk.Button(root, text="Cerrar", command=self.close)
        self.btn_exit.pack()

    def update_frame(self):
        """Captura un frame de la cámara y lo actualiza en la interfaz."""
        stream = io.BytesIO()
        self.camera.capture(stream, format='jpeg', use_video_port=True)
        stream.seek(0)
        
        image = Image.open(stream)
        image = ImageTk.PhotoImage(image)
        
        self.label.configure(image=image)
        self.label.image = image
        
        self.root.after(10, self.update_frame)

    def close(self):
        boton_ejecutar.config(state=tk.NORMAL)
        boton_camara.config(state=tk.NORMAL)
        """Cierra la aplicación y libera la cámara."""
        self.camera.close()
        self.root.destroy()

def abrir_camara():
    
    valor_isx = entry_isx.get()
    if not valor_isx or not valor_isx.isdigit():
        messagebox.showerror("Error", "No se ha definido el valor de ISO.")
        return
    
    boton_ejecutar.config(state=tk.DISABLED)
    boton_camara.config(state=tk.DISABLED)
    """Abre la ventana de la cámara en directo."""
    camera_window = tk.Toplevel(ventana)
    camera_window.protocol("WM_DELETE_WINDOW", lambda: None)
    CameraApp(camera_window)

# Crear la interfaz gráfica
crear_csv_si_no_existe()
ventana = tk.Tk()
ventana.title("LitoScan.AR")

# Configurar tamaño de la ventana
ventana.geometry("1200x900")

# Crear un frame para el título y el logo
frame_titulo = tk.Frame(ventana)
frame_titulo.pack(pady=10)

# Título en el lateral izquierdo
etiqueta_titulo = tk.Label(frame_titulo, text="LitoScan.AR", font=("Arial", 20, "bold"))
etiqueta_titulo.pack()

# Cargar y mostrar el logo
logo = tk.PhotoImage(file="assets/logo.png")
label_logo = tk.Label(frame_titulo, image=logo)
label_logo.pack()

# Entrada de datos
frame_entrada = tk.Frame(ventana)
frame_entrada.pack(pady=10)

# Nombre de la configuración
tk.Label(frame_entrada, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
entry_nombre = tk.Entry(frame_entrada)
entry_nombre.grid(row=0, column=1, padx=5, pady=5)

# x_home y y_home en la misma fila
tk.Label(frame_entrada, text="x_home:").grid(row=1, column=0, padx=5, pady=5)
entry_x_home = tk.Entry(frame_entrada)
entry_x_home.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_entrada, text="y_home:").grid(row=1, column=2, padx=5, pady=5)
entry_y_home = tk.Entry(frame_entrada)
entry_y_home.grid(row=1, column=3, padx=5, pady=5)

# num_x y num_y en la misma fila
tk.Label(frame_entrada, text="num_x:").grid(row=2, column=0, padx=5, pady=5)
entry_num_x = tk.Entry(frame_entrada)
entry_num_x.grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame_entrada, text="num_y:").grid(row=2, column=2, padx=5, pady=5)
entry_num_y = tk.Entry(frame_entrada)
entry_num_y.grid(row=2, column=3, padx=5, pady=5)

# x_ini, x_max, y_ini, y_max en la misma fila
tk.Label(frame_entrada, text="x_ini:").grid(row=3, column=0, padx=5, pady=5)
entry_x_ini = tk.Entry(frame_entrada)
entry_x_ini.grid(row=3, column=1, padx=5, pady=5)

tk.Label(frame_entrada, text="x_max:").grid(row=3, column=2, padx=5, pady=5)
entry_x_max = tk.Entry(frame_entrada)
entry_x_max.grid(row=3, column=3, padx=5, pady=5)

tk.Label(frame_entrada, text="y_ini:").grid(row=3, column=4, padx=5, pady=5)
entry_y_ini = tk.Entry(frame_entrada)
entry_y_ini.grid(row=3, column=5, padx=5, pady=5)

tk.Label(frame_entrada, text="y_max:").grid(row=3, column=6, padx=5, pady=5)
entry_y_max = tk.Entry(frame_entrada)
entry_y_max.grid(row=3, column=7, padx=5, pady=5)

# focus_pos en su propia fila
tk.Label(frame_entrada, text="focus_pos:").grid(row=4, column=0, padx=5, pady=5)
entry_focus_pos = tk.Entry(frame_entrada)
entry_focus_pos.grid(row=4, column=1, padx=5, pady=5)



# isx en su propia fila
tk.Label(frame_entrada, text="isx:").grid(row=6, column=0, padx=5, pady=5)
entry_isx = tk.Entry(frame_entrada)
entry_isx.grid(row=6, column=1, padx=5, pady=5)

# res_x y res_y en la misma fila
tk.Label(frame_entrada, text="res_x:").grid(row=7, column=0, padx=5, pady=5)
entry_res_x = tk.Entry(frame_entrada)
entry_res_x.grid(row=7, column=1, padx=5, pady=5)

tk.Label(frame_entrada, text="res_y:").grid(row=7, column=2, padx=5, pady=5)
entry_res_y = tk.Entry(frame_entrada)
entry_res_y.grid(row=7, column=3, padx=5, pady=5)

# Carpeta en su propia fila
tk.Label(frame_entrada, text="Carpeta:").grid(row=20, column=0, padx=5, pady=5)
entry_carpeta = tk.Entry(frame_entrada)
entry_carpeta.grid(row=20, column=1, padx=5, pady=5)

# Crear la tabla
columns = ("Nombre", "x_home", "y_home", "num_x", "num_y", "x_ini", "x_max", "y_ini", "y_max", "focus_pos","isx", "res_x", "res_y")
tree = ttk.Treeview(ventana, columns=columns, show="headings", height=5) 
for col in columns:
    tree.heading(col, text=col)
tree.pack()

# Agregar botones en una misma fila
frame_botones = tk.Frame(ventana)
frame_botones.pack(pady=10)

# Botón para guardar configuración
boton_agregar = tk.Button(frame_botones, text="Agregar Configuración", command=agregar_configuracion)
boton_agregar.grid(row=0, column=0, padx=5, pady=5)

# Botón para mostrar eliminar configuración
boton_eliminar = tk.Button(frame_botones, text="Eliminar Configuración", command=eliminar_configuracion)
boton_eliminar.grid(row=0, column=1, padx=5, pady=5)

# Botón para importar configuración
boton_importar = tk.Button(frame_botones, text="Importar Configuración", command=importar_configuracion)
boton_importar.grid(row=0, column=2, padx=5, pady=5)

# Botón para abrir la cámara
boton_camara = tk.Button(frame_botones, text="Cámara Pi", command=abrir_camara)
boton_camara.grid(row=0, column=3, padx=5, pady=5)

# Botón para mostrar información
boton_info = tk.Button(frame_botones, text="Información", command=show_info)
boton_info.grid(row=0, column=4, padx=5, pady=5)

# Botón para iniciar el subproceso
boton_ejecutar = tk.Button(ventana, text="Iniciar", command=ejecutar_codigo)
boton_ejecutar.pack(pady=10)  # Este es el nuevo botón

# Etiqueta para mostrar estado
etiqueta_estado = tk.Label(ventana, text="En espera", fg="black")
etiqueta_estado.pack(pady=10)


refrescar_tabla()

ventana.mainloop()
