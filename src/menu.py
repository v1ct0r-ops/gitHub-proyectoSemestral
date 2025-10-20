import tkinter as tk
from tkinter import messagebox
from database.database import conectar

class MenuApp:
    def __init__(self, master, usuario, callback_crear_orden=None, callback_cerrar_sesion=None):
        self.master = master
        self.usuario = usuario
        self.callback_crear_orden = callback_crear_orden  # Guardar callback para crear orden
        self.callback_cerrar_sesion = callback_cerrar_sesion  # Guardar callback para cerrar sesión
        master.title("Menú Principal")
        master.geometry("400x300")
        self.crear_interfaz()

    def crear_interfaz(self):
        tk.Label(self.master, text=f"Bienvenido, {self.usuario}", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.master, text="Crear nueva orden", width=25, command=self.crear_orden).pack(pady=10)
        tk.Button(self.master, text="Listar órdenes guardadas", width=25, command=self.listar_ordenes).pack(pady=10)
        tk.Button(self.master, text="Cerrar sesión", width=25, command=self.cerrar_sesion).pack(pady=10)

    def crear_orden(self):
        """Ejecutar callback para crear orden o mostrar mensaje por defecto"""
        if self.callback_crear_orden:
            self.callback_crear_orden()  # Llamar al callback de app.py
        else:
            messagebox.showinfo("Función", "Aquí se abriría el formulario de nueva orden.")
            # Modo independiente (sin integración)

    def listar_ordenes(self):
        conexion = conectar()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT numero_orden, cliente, precios, fecha_creacion FROM ordenes_compra ORDER BY fecha_creacion DESC")
            ordenes = cursor.fetchall()
            conexion.close()
            if ordenes:
                listado = "\n".join([f"N°{o[0]} | Cliente: {o[1]} | Total: ${o[2]:,} | Fecha: {o[3]}" for o in ordenes])
                messagebox.showinfo("Órdenes guardadas", listado)
            else:
                messagebox.showinfo("Órdenes guardadas", "No hay órdenes registradas.")
        else:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos.")

    def cerrar_sesion(self):
        """Ejecutar callback para cerrar sesión o cerrar ventana por defecto"""
        if self.callback_cerrar_sesion:
            self.callback_cerrar_sesion()  # Llamar al callback de app.py
        else:
            self.master.destroy()  # Modo independiente

if __name__ == "__main__":
    root = tk.Tk()
    app = MenuApp(root, "admin")  # Cambia "admin" por el usuario logueado
    root.mainloop()
