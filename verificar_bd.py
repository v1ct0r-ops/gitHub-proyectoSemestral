#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar rápidamente las órdenes guardadas en la base de datos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database.database import conectar

def verificar_ordenes():
    """Verifica y muestra todas las órdenes guardadas"""
    print("🔍 VERIFICANDO BASE DE DATOS...")
    print("=" * 60)
    
    conexion = conectar()
    if not conexion:
        print("❌ Error: No se pudo conectar a la base de datos")
        return
    
    try:
        cursor = conexion.cursor()
        
        # Contar total de órdenes
        cursor.execute("SELECT COUNT(*) FROM ordenes_compra")
        total_ordenes = cursor.fetchone()[0]
        
        print(f"📊 TOTAL DE ÓRDENES: {total_ordenes}")
        print("-" * 60)
        
        if total_ordenes == 0:
            print("📭 No hay órdenes guardadas aún")
            return
        
        # Mostrar todas las órdenes
        cursor.execute("""
            SELECT id, numero_orden, cliente, direccion, telefono, 
                   comuna, region, productos, precios, fecha_creacion 
            FROM ordenes_compra 
            ORDER BY fecha_creacion DESC
        """)
        ordenes = cursor.fetchall()
        
        for i, orden in enumerate(ordenes, 1):
            print(f"🛒 ORDEN #{i}")
            print(f"   ID: {orden[0]}")
            print(f"   Número: {orden[1]}")
            print(f"   Cliente: {orden[2]}")
            print(f"   Dirección: {orden[3]}")
            print(f"   Teléfono: {orden[4]}")
            print(f"   Comuna: {orden[5]}")
            print(f"   Región: {orden[6]}")
            print(f"   Productos: {orden[7]}")
            print(f"   Total: ${orden[8]:,}")
            print(f"   Fecha: {orden[9]}")
            print("-" * 60)
        
        conexion.close()
        
    except Exception as e:
        print(f"❌ Error al consultar base de datos: {e}")

if __name__ == "__main__":
    verificar_ordenes()
    input("\nPresiona Enter para continuar...")