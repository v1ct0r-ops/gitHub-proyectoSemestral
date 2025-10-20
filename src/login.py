import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

#  directorio padre al path para importar database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.database import conectar

class LoginApp:
    def __init__(self, root, callback_login_exitoso=None):
        self.root = root
        self.callback_login_exitoso = callback_login_exitoso  # Guardar el callback
        self.root.title("Login")
        self.root.geometry("300x200")
        
        self.frame = ttk.Frame(root, padding="10")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.label_username = ttk.Label(self.frame, text="Usuario:")
        self.label_username.pack(pady=5)
        
        self.entry_username = ttk.Entry(self.frame)
        self.entry_username.pack(pady=5)
        
        self.label_password = ttk.Label(self.frame, text="Contraseña:")
        self.label_password.pack(pady=5)
        
        self.entry_password = ttk.Entry(self.frame, show="*")
        self.entry_password.pack(pady=5)
        
        self.button_login = ttk.Button(self.frame, text="Ingresar", command=self.login)
        self.button_login.pack(pady=10)
    
    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Introduzca usuario  y contraseña.")
            return
        
        conexion = conectar()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT password_hash FROM usuarios WHERE username=?", (username,))
            result = cursor.fetchone()
            conexion.close()
            
            if result:
                # Hashear la contraseña ingresada para compararla
                import hashlib
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                if result[0] == password_hash:
                    messagebox.showinfo("Success", "Login successful!")
                    
                    # Si hay callback, llamarlo con el usuario
                    if self.callback_login_exitoso:
                        self.callback_login_exitoso(username)
                    else:
                        # Si no hay callback, cerrar ventana (modo independiente)
                        self.root.destroy()
                else:
                    messagebox.showerror("Error", "usuario o contraseña invalida.")
            else:
                messagebox.showerror("Error", "usuario o contraseña invalida.")
        else:
            messagebox.showerror("Error", "conexion a base de datos fallida.")

# Código para probar el login
if __name__ == "__main__":
    root = tk.Tk()   #me permite crear la ventana principal
    app = LoginApp(root)    # creo el sistema de login dentro de esta ventana
    root.mainloop()   # mantengo la ventana abierta y funciionando

        