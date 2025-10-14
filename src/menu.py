import tkinter as tk
from tkinter import messagebox
from database.database import conectar

class MenuApp:
    def __init__(self, master, usuario):
        self.master = master
        self.usuario = usuario
        master.title("Menú Principal")
        master.geometry("400x300")
        self.crear_interfaz()

    def crear_interfaz(self):
        tk.Label(self.master, text=f"Bienvenido, {self.usuario}", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.master, text="Crear nueva orden", width=25, command=self.crear_orden).pack(pady=10)
        tk.Button(self.master, text="Listar órdenes guardadas", width=25, command=self.listar_ordenes).pack(pady=10)
        tk.Button(self.master, text="Cerrar sesión", width=25, command=self.cerrar_sesion).pack(pady=10)

    def crear_orden(self):
        messagebox.showinfo("Función", "Aquí se abriría el formulario de nueva orden.")
        # Aquí se debe integrar con OrdenCompraApp

    def listar_ordenes(self):
        conexion = conectar()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT numero_orden, cliente, total, fecha_creacion FROM ordenes_compra ORDER BY fecha_creacion DESC")
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
        self.master.destroy()
        # Aquí se debe regresar al login

if __name__ == "__main__":
    root = tk.Tk()
    app = MenuApp(root, "admin")  # Cambia "admin" por el usuario logueado
    root.mainloop()
