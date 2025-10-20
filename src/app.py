import tkinter as tk
import sys
import os

# Agregar el directorio padre al path para encontrar el módulo database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import inicializar_base_de_datos

class SistemaGestionOrdenes:
    def __init__(self):
        self.ventana_actual = None
        self.usuario_logueado = None
        
    def iniciar_aplicacion(self):
        """Punto de entrada principal del sistema"""
        print(" Iniciando Sistema de Gestión de Órdenes...")
        
        # 1. Inicializar base de datos
        inicializar_base_de_datos()
        print(" Base de datos inicializada")
        
        # 2. Mostrar ventana de login
        self.mostrar_login()
        
    def mostrar_login(self):
        """Muestra la ventana de login"""
        print("🔐 Mostrando ventana de login...")
        from src.login import LoginApp
        
        # Crear ventana para el login
        root = tk.Tk()
        self.ventana_actual = root
        
        # Crear el login y pasarle una función callback
        login_app = LoginApp(root, self.on_login_exitoso)
        
        # Iniciar el loop de la ventana
        root.mainloop()
        
    def on_login_exitoso(self, usuario):
        """Callback que se ejecuta cuando el login es exitoso"""
        print(f" Login exitoso para usuario: {usuario}")
        self.usuario_logueado = usuario
        
        # Cerrar ventana de login
        self.ventana_actual.destroy()
        
        # Abrir menú principal
        self.mostrar_menu()
        
    def mostrar_menu(self):
        """Muestra el menú principal"""
        print(f"📋 Abriendo menú para {self.usuario_logueado}...")
        from src.menu import MenuApp
        
        # Crear ventana para el menú
        root = tk.Tk()
        self.ventana_actual = root
        
        # Crear el menú con callbacks para cada opción
        menu_app = MenuApp(
            root, 
            self.usuario_logueado,
            callback_crear_orden=self.on_crear_orden,
            callback_cerrar_sesion=self.on_cerrar_sesion
        )
        
        # Iniciar el loop de la ventana
        root.mainloop()
        
    def on_crear_orden(self):
        """Callback cuando el usuario quiere crear una orden"""
        print("📝 Usuario quiere crear nueva orden...")
        
        # Cerrar ventana del menú
        self.ventana_actual.destroy()
        
        # Abrir formulario de orden
        self.mostrar_formulario_orden()
        
    def on_cerrar_sesion(self):
        """Callback cuando el usuario quiere cerrar sesión"""
        print("👋 Usuario quiere cerrar sesión...")
        
        # Cerrar ventana del menú
        self.ventana_actual.destroy()
        
        # Resetear usuario
        self.usuario_logueado = None
        
        # Volver al login
        self.mostrar_login()
        
    def mostrar_formulario_orden(self):
        """Muestra el formulario de nueva orden"""
        print("📋 Abriendo formulario de orden...")
        from src.orden_compra import OrdenCompraApp
        
        # Crear ventana para el formulario
        root = tk.Tk()
        self.ventana_actual = root
        
        # Crear el formulario con callbacks
        orden_app = OrdenCompraApp(
            root,
            callback_orden_guardada=self.on_orden_guardada,
            callback_volver_menu=self.on_volver_menu
        )
        
        # Iniciar el loop de la ventana
        root.mainloop()
        
    def on_orden_guardada(self):
        """Callback cuando se guarda una orden exitosamente"""
        print("✅ Orden guardada exitosamente, volviendo al menú...")
        
        # Cerrar formulario
        self.ventana_actual.destroy()
        
        # Volver al menú
        self.mostrar_menu()
        
    def on_volver_menu(self):
        """Callback cuando quieren volver al menú sin guardar"""
        print("⬅️ Volviendo al menú...")
        
        # Cerrar formulario
        self.ventana_actual.destroy()
        
        # Volver al menú
        self.mostrar_menu()

if __name__ == "__main__":
    sistema = SistemaGestionOrdenes()
    sistema.iniciar_aplicacion()