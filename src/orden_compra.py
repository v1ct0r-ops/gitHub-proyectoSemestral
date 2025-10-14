import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime

#Importo la base de datos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.database import conectar

class OrdenCompraApp:
    def __init__(self,root):
        self.root = root
        self.root.title("Sistema gas Licuado - Orden de Compra")
        self.root.geometry("600x700")
        
        # Cargar productos desde BD
        self.productos = self.cargar_productos()
        
        # Crear la interfaz
        self.crear_interfaz()
    
    def cargar_productos(self):
        """Carga productos y precios desde la base de datos"""
        conexion = conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("SELECT nombre, precio FROM productos WHERE activo = 1")
                productos = cursor.fetchall()
                conexion.close()
                return dict(productos)  # {"Galón 5kg": 8500, ...}
            except Exception as e:
                print(f"Error al cargar productos: {e}")
                conexion.close()
                return {}
        return {}
    
    def crear_interfaz(self):
        """Crea todos los elementos de la interfaz"""
        # Frame principal con scroll
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = ttk.Label(main_frame, text="Registro de Orden de Compra", 
                          font=("Arial", 16, "bold"))
        titulo.pack(pady=(0, 20))
        
        # === SECCIÓN 1: DATOS DE LA ORDEN ===
        orden_frame = ttk.LabelFrame(main_frame, text="Datos de la Orden", padding="10")
        orden_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Número de orden (auto-generado)
        ttk.Label(orden_frame, text="Número de Orden:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.numero_orden = tk.StringVar(value=f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        ttk.Entry(orden_frame, textvariable=self.numero_orden, state="readonly", width=25).grid(row=0, column=1, sticky=tk.W, padx=(10,0))
        
        # === SECCIÓN 2: DATOS DEL CLIENTE ===
        cliente_frame = ttk.LabelFrame(main_frame, text="Datos del Cliente", padding="10")
        cliente_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Cliente
        ttk.Label(cliente_frame, text="Nombre del Cliente:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.cliente = tk.StringVar()
        ttk.Entry(cliente_frame, textvariable=self.cliente, width=40).grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=(10,0))
        
        # Teléfono
        ttk.Label(cliente_frame, text="Teléfono:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.telefono = tk.StringVar()
        ttk.Entry(cliente_frame, textvariable=self.telefono, width=20).grid(row=1, column=1, sticky=tk.W, padx=(10,0))
        
        # Dirección
        ttk.Label(cliente_frame, text="Dirección:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.direccion = tk.StringVar()
        ttk.Entry(cliente_frame, textvariable=self.direccion, width=50).grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=(10,0))
        
        # Comuna y Región
        ttk.Label(cliente_frame, text="Comuna:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.comuna = tk.StringVar()
        ttk.Entry(cliente_frame, textvariable=self.comuna, width=25).grid(row=3, column=1, sticky=tk.W, padx=(10,0))
        
        ttk.Label(cliente_frame, text="Región:").grid(row=3, column=2, sticky=tk.W, pady=5, padx=(20,0))
        self.region = tk.StringVar()
        ttk.Entry(cliente_frame, textvariable=self.region, width=25).grid(row=3, column=3, sticky=tk.W, padx=(10,0))
        
        # === SECCIÓN 3: PRODUCTOS DE GAS LICUADO ===
        productos_frame = ttk.LabelFrame(main_frame, text="Productos de Gas Licuado", padding="10")
        productos_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Headers
        ttk.Label(productos_frame, text="Tipo de Galón", font=("Arial", 10, "bold")).grid(row=0, column=0, pady=5)
        ttk.Label(productos_frame, text="Precio Unitario", font=("Arial", 10, "bold")).grid(row=0, column=1, pady=5)
        ttk.Label(productos_frame, text="Cantidad", font=("Arial", 10, "bold")).grid(row=0, column=2, pady=5)
        ttk.Label(productos_frame, text="Subtotal", font=("Arial", 10, "bold")).grid(row=0, column=3, pady=5)
        
        # Crear campos para cada producto
        self.cantidades = {}
        self.subtotales = {}
        row = 1
        
        for producto, precio in self.productos.items():
            # Nombre del producto
            ttk.Label(productos_frame, text=producto).grid(row=row, column=0, sticky=tk.W, pady=2)
            
            # Precio
            ttk.Label(productos_frame, text=f"${precio:,}").grid(row=row, column=1, pady=2)
            
            # Cantidad
            self.cantidades[producto] = tk.StringVar(value="0")
            cantidad_entry = ttk.Entry(productos_frame, textvariable=self.cantidades[producto], width=10)
            cantidad_entry.grid(row=row, column=2, padx=10, pady=2)
            
            # Subtotal
            self.subtotales[producto] = tk.StringVar(value="$0")
            ttk.Label(productos_frame, textvariable=self.subtotales[producto]).grid(row=row, column=3, pady=2)
            
            # Conectar evento para calcular subtotal automáticamente
            self.cantidades[producto].trace('w', lambda *args, p=producto: self.calcular_subtotal(p))
            
            row += 1
        
        # === TOTAL GENERAL ===
        total_frame = ttk.Frame(productos_frame)
        total_frame.grid(row=row, column=0, columnspan=4, pady=(10, 0), sticky=tk.E)
        
        ttk.Label(total_frame, text="TOTAL GENERAL:", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        self.total_general = tk.StringVar(value="$0")
        ttk.Label(total_frame, textvariable=self.total_general, font=("Arial", 12, "bold"), foreground="blue").pack(side=tk.LEFT, padx=(10, 0))
        
        # === SECCIÓN 4: BOTONES DE ACCIÓN ===
        botones_frame = ttk.Frame(main_frame)
        botones_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Botón Guardar Orden
        ttk.Button(botones_frame, text="Guardar Orden", command=self.guardar_orden, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón Limpiar Formulario
        ttk.Button(botones_frame, text="Limpiar Formulario", command=self.limpiar_formulario).pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón Ver Órdenes Guardadas
        ttk.Button(botones_frame, text="Ver Órdenes Guardadas", command=self.ver_ordenes).pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón Cancelar
        ttk.Button(botones_frame, text="Cancelar", command=self.root.destroy).pack(side=tk.RIGHT)
        
        # Aquí agregaremos todos los campos
        print("Productos cargados:", self.productos)
    
    def calcular_subtotal(self, producto):
        """Calcula el subtotal cuando cambia la cantidad"""
        try:
            cantidad = int(self.cantidades[producto].get() or 0)
            precio = self.productos[producto]
            subtotal = cantidad * precio
            self.subtotales[producto].set(f"${subtotal:,}")
            self.calcular_total_general()
        except ValueError:
            self.subtotales[producto].set("$0")
            self.calcular_total_general()
    
    def calcular_total_general(self):
        """Calcula el total general de todos los productos"""
        total = 0
        for producto in self.productos:
            try:
                cantidad = int(self.cantidades[producto].get() or 0)
                precio = self.productos[producto]
                total += cantidad * precio
            except ValueError:
                pass
        self.total_general.set(f"${total:,}")
    
    def guardar_orden(self):
        """Guarda la orden en la base de datos"""
        # Validar campos obligatorios
        if not self.cliente.get().strip():
            messagebox.showerror("Error", "El nombre del cliente es obligatorio")
            return
        
        if not self.telefono.get().strip():
            messagebox.showerror("Error", "El teléfono es obligatorio")
            return
        
        if not self.direccion.get().strip():
            messagebox.showerror("Error", "La dirección es obligatoria")
            return
        
        # Verificar que se seleccionó al menos un producto
        productos_seleccionados = []
        total_orden = 0
        
        for producto, cantidad_var in self.cantidades.items():
            try:
                cantidad = int(cantidad_var.get() or 0)
                if cantidad > 0:
                    precio = self.productos[producto]
                    productos_seleccionados.append(f"{producto}: {cantidad} unidades")
                    total_orden += cantidad * precio
            except ValueError:
                pass
        
        if not productos_seleccionados:
            messagebox.showerror("Error", "Debe seleccionar al menos un producto")
            return
        
        # Guardar en base de datos
        conexion = conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute("""
                    INSERT INTO ordenes_compra 
                    (numero_orden, cliente, direccion, telefono, comuna, region, productos, precios)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.numero_orden.get(),
                    self.cliente.get(),
                    self.direccion.get(),
                    self.telefono.get(),
                    self.comuna.get(),
                    self.region.get(),
                    " | ".join(productos_seleccionados),
                    total_orden
                ))
                conexion.commit()
                conexion.close()
                
                messagebox.showinfo("Éxito", f"Orden guardada correctamente\nTotal: ${total_orden:,}")
                self.limpiar_formulario()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {e}")
                conexion.close()
    
    def limpiar_formulario(self):
        """Limpia todos los campos del formulario"""
        # Generar nuevo número de orden
        self.numero_orden.set(f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        # Limpiar datos del cliente
        self.cliente.set("")
        self.telefono.set("")
        self.direccion.set("")
        self.comuna.set("")
        self.region.set("")
        
        # Limpiar cantidades
        for cantidad_var in self.cantidades.values():
            cantidad_var.set("0")
    
    def ver_ordenes(self):
        """Muestra una ventana con todas las órdenes guardadas"""
        ventana_ordenes = tk.Toplevel(self.root)
        ventana_ordenes.title("Órdenes Guardadas")
        ventana_ordenes.geometry("900x600")
        
        # Crear frame principal con scrollbar
        main_frame = ttk.Frame(ventana_ordenes)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        ttk.Label(main_frame, text="📋 ÓRDENES GUARDADAS", font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Crear Treeview para mostrar las órdenes
        columns = ("ID", "Número", "Cliente", "Dirección", "Teléfono", "Total", "Fecha")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        # Definir encabezados y anchos
        tree.heading("ID", text="ID")
        tree.heading("Número", text="N° Orden")
        tree.heading("Cliente", text="Cliente")
        tree.heading("Dirección", text="Dirección")
        tree.heading("Teléfono", text="Teléfono")
        tree.heading("Total", text="Total")
        tree.heading("Fecha", text="Fecha")
        
        tree.column("ID", width=50)
        tree.column("Número", width=120)
        tree.column("Cliente", width=150)
        tree.column("Dirección", width=200)
        tree.column("Teléfono", width=100)
        tree.column("Total", width=100)
        tree.column("Fecha", width=150)
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar_y.set)
        
        # Empaquetar tree y scrollbar
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame para botones
        botones_frame = ttk.Frame(ventana_ordenes)
        botones_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Cargar datos desde la base de datos
        try:
            conexion = conectar()
            if conexion:
                cursor = conexion.cursor()
                cursor.execute("""
                    SELECT id, numero_orden, cliente, direccion, telefono, precios, fecha_creacion 
                    FROM ordenes_compra 
                    ORDER BY fecha_creacion DESC
                """)
                ordenes = cursor.fetchall()
                
                if ordenes:
                    for orden in ordenes:
                        # Formatear el total con separador de miles
                        total_formateado = f"${orden[5]:,}"
                        # Formatear fecha
                        fecha_formateada = orden[6][:16] if len(orden[6]) > 16 else orden[6]
                        
                        tree.insert("", "end", values=(
                            orden[0], orden[1], orden[2], orden[3][:30] + "..." if len(orden[3]) > 30 else orden[3], 
                            orden[4], total_formateado, fecha_formateada
                        ))
                    
                    # Label con total de órdenes
                    ttk.Label(botones_frame, text=f"Total de órdenes: {len(ordenes)}", 
                             font=("Arial", 10, "bold")).pack(side=tk.LEFT)
                else:
                    tree.insert("", "end", values=("", "", "No hay órdenes guardadas", "", "", "", ""))
                
                conexion.close()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar órdenes: {str(e)}")
        
        # Botón para cerrar
        ttk.Button(botones_frame, text="Cerrar", command=ventana_ordenes.destroy).pack(side=tk.RIGHT)

# Código de prueba
if __name__ == "__main__":
    root = tk.Tk()
    app = OrdenCompraApp(root)
    root.mainloop()